import discord
import discord.ext.commands as cmd
from config import (
    MENTION_CH_ID,
    ADMIN_ID,
    PROTECTED_ROLE_IDS,
)
from libraries.error import (
    UnexpectedDataError,
    BotChannelError,
)
from libraries.checks import is_bot_channel

class RolesCog(cmd.Cog):
    _join_emoji = '☑'

    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='create')
    @is_bot_channel()
    async def create_mention_group(self, ctx, *, role_name: str):
        if any(role.name.lower() == role_name.lower() for role in ctx.guild.roles):
            await ctx.send(f'Cannot create another group with the name "{role_name}"')
            return

        role = await ctx.guild.create_role(name=role_name, mentionable=True, reason="Created through command")

        mention_ch = ctx.guild.get_channel(MENTION_CH_ID)
        msg = await mention_ch.send(f'**\*\*Join\*\*** {role.mention}')
        await msg.add_reaction(self._join_emoji)

        await ctx.send(f'"{role_name}" created successfully')

    @create_mention_group.error
    async def create_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'role_name':
                await ctx.send('Cannot specify a role with an empty name')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.Cog.listener(name='on_reaction_add')
    async def join_mention_group(self, reaction, user):
        if user == self.bot.user:
            return

        msg = reaction.message
        if msg.channel.id != MENTION_CH_ID:
            return

        if reaction.emoji != self._join_emoji:
            return

        if len(msg.role_mentions) != 1:
            admin = user.guild.get_member(ADMIN_ID)
            await admin.send(
                f'{user} attempted to join role from message "{msg.content}". '
                f'Failed because message has {len(msg.role_mentions)} roles mentioned'
            )
            raise UnexpectedDataError(f'Message "{msg.content}" has {len(msg.role_mentions)} roles mentioned')

        role = msg.role_mentions[0]
        
        if role in user.roles:
            return

        if role.id in PROTECTED_ROLE_IDS or not role.mentionable:
            return

        await user.add_roles(role, reason='Bot command', atomic=True)


    @cmd.Cog.listener(name='on_reaction_remove')
    async def leave_mention_group(self, reaction, user):
        if user == self.bot.user:
            return

        msg = reaction.message
        if msg.channel.id != MENTION_CH_ID:
            return

        if reaction.emoji != self._join_emoji:
            return

        if len(msg.role_mentions) != 1:
            admin = user.guild.get_member(ADMIN_ID)
            await admin.send(
                f'{user} attempted to leave role from message "{msg.content}". '
                f'Failed because message has {len(msg.role_mentions)} roles mentioned'
            )
            raise UnexpectedDataError(f'Message "{msg.content}" has {len(msg.role_mentions)} roles mentioned')

        role = msg.role_mentions[0]
        
        if role not in user.roles:
            return

        if role.id in PROTECTED_ROLE_IDS or not role.mentionable:
            return

        await user.remove_roles(role, reason='Bot command', atomic=True)


    @cmd.command(name='delete')
    @is_bot_channel()
    async def delete_mention_group(self, ctx, *, role:discord.Role):
        if role not in ctx.guild.roles:
            await ctx.send(f'{role} no longer exists')
            return

        if role.id in PROTECTED_ROLE_IDS or not role.mentionable:
            await ctx.send(f'{role} cannot be deleted')
            return

        mention_ch = ctx.guild.get_channel(MENTION_CH_ID)

        role_join_msg = None
        async for msg in mention_ch.history():
            if len(msg.role_mentions) == 1 and msg.role_mentions[0] == role:
                role_join_msg = msg
                break

        if not role_join_msg:
            await ctx.send(f'{role} is not a deletable mention group')

        reaction = (
            reaction
            for reaction in role_join_msg.reactions
            if reaction.emoji == self._join_emoji
        )
        reaction = next(reaction, None)

        if reaction:
            if reaction.count > 1:
                await ctx.send(f'{role} cannot be deleted while other users are in it')
                return

            users = await reaction.users().flatten()
            if any(user != self.bot.user for user in users):
                await ctx.send(f'{role} cannot be deleted while other users are in it')
                return

        await role.delete(reason='Bot command')
        await role_join_msg.delete()
        await ctx.send('Role deleted successfully!')

    @delete_mention_group.error
    async def delete_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'role':
                await ctx.send('Must specify a role to delete')
        else:
            await self.bot.handle_error(ctx, error)


def setup(bot):
    bot.add_cog(RolesCog(bot))
