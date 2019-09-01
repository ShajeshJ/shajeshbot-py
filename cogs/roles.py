import discord
import discord.ext.commands as cmd
from config import MENTION_CHANNEL as mention_ch_id
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
        mention_ch = ctx.guild.get_channel(mention_ch_id)
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
            raise UnexpectedDataError(f'Message "{content}" has {len(msg.role_mentions)} roles mentioned')

        role = msg.role_mentions[0]
        
        if role in user.roles:
            await user.send(f'You are already in the mention group "{role.name}"')
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
            raise UnexpectedDataError(f'Message "{content}" {len(msg.role_mentions)} roles mentioned')

        role = msg.role_mentions[0]
        
        if role not in user.roles:
            await user.send(f'You are not in the mention group "{role.name}"')
            return

        await user.remove_roles(role, reason='Bot command', atomic=True)


    @cmd.command(name='delete')
    async def delete_mention_group(self, ctx: cmd.Context, *, role:discord.Role):
        pass

    @cmd.command(name='members')
    async def list_group_members(self, ctx: cmd.Context, *, role:discord.Role):
        pass


    @cmd.command(name='list')
    async def list_mention_groups(self, ctx: cmd.Context):
        pass


def setup(bot):
    bot.add_cog(RolesCog(bot))
