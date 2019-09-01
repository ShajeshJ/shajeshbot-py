import discord
import discord.ext.commands as cmd
from config import MENTION_CH_ID, ADMIN_ID
from error import UnexpectedDataError

class RolesCog(cmd.Cog, name='Roles'):
    _join_emoji = '☑'

    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='create')
    async def create_mention_group(self, ctx: cmd.Context, *, role_name: str):
        if any(role.name.lower() == role_name.lower() for role in ctx.guild.roles):
            await ctx.send(f'Cannot create another group with the name "{role_name}"')
            return

        role = await ctx.guild.create_role(name=role_name, mentionable=True, reason="Created through command")
        mention_ch = ctx.guild.get_channel(MENTION_CH_ID)
        msg = await mention_ch.send(f'Join {role.mention}')
        await msg.add_reaction(self._join_emoji)
        await ctx.send(f'"{role_name}" created successfully')


    @create_mention_group.error
    async def create_error_handler(self, ctx: cmd.Context, error: cmd.CommandError):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'role_name':
                await ctx.send('Cannot specify a role with an empty name')
        else:
            raise error


    @cmd.Cog.listener(name='on_reaction_add')
    async def join_mention_group(self, reaction, user):
        if user == self.bot.user:
            return

        msg = reaction.message
        if msg.channel.id != mention_ch_id:
            return

        if reaction.emoji != self._join_emoji:
            return

        if len(msg.role_mentions) != 1:
            admin = ctx.guild.get_member(ADMIN_ID)
            await admin.send(
                f'{ctx.author} attempted to join role from message "{msg.content}". '
                f'Failed because message has {len(msg.role_mentions)} roles mentioned'
            )
            raise UnexpectedDataError(f'Message "{msg.content}" has {len(msg.role_mentions)} roles mentioned')

        role = msg.role_mentions[0]
        
        if role in user.roles:
            return

        await user.add_roles(role, reason='Bot command', atomic=True)


    @cmd.Cog.listener(name='on_reaction_remove')
    async def leave_mention_group(self, reaction, user):
        if user == self.bot.user:
            return

        msg = reaction.message
        if msg.channel.id != mention_ch_id:
            return

        if reaction.emoji != self._join_emoji:
            return

        if len(msg.role_mentions) != 1:
            admin = ctx.guild.get_member(ADMIN_ID)
            await admin.send(
                f'{ctx.author} attempted to leave role from message "{msg.content}". '
                f'Failed because message has {len(msg.role_mentions)} roles mentioned'
            )
            raise UnexpectedDataError(f'Message "{msg.content}" has {len(msg.role_mentions)} roles mentioned')

        role = msg.role_mentions[0]
        
        if role not in user.roles:
            return

        await user.remove_roles(role, reason='Bot command', atomic=True)


    @cmd.command(name='delete')
    async def delete_mention_group(self, ctx: cmd.Context, *, role:discord.Role):
        pass


def setup(bot):
    bot.add_cog(RolesCog(bot))
