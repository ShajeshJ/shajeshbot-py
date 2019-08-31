import discord
import discord.ext.commands as cmd

class RolesCog(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='create')
    async def create_mention_group(self, ctx: cmd.Context, *, role_name: str):
        if not role_name:
            await ctx.send('Cannot specify a role with an empty name')
            return

        guild: discord.Guild = ctx.guild

        if any(role.name.lower() == role_name.lower() for role in guild.roles):
            await ctx.send(f'Cannot create another group with the name "{role_name}"')
            return

        await guild.create_role(name=role_name, mentionable=True, reason="Created through command")
        await ctx.send(f'"{role_name}" created successfully')


    @cmd.command(name='join')
    async def join_mention_group(self, ctx:cmd.Context, *, role: discord.Role):
        pass


    @cmd.command(name='leave')
    async def leave_mention_group(self, ctx: cmd.Context, *, role:discord.Role):
        pass


    @cmd.command(name='delete')
    async def delete_mention_group(self, ctx: cmd.Context, *, role:discord.Role):
        pass

    @cmd.command(name='members')
    async def list_group_members(self, ctx: cmd.Context, *, role:discord.Role):
        pass


    @cmd.command(name='list')
    async def list_mention_groups(self, ctx: cmd.Context):
        pass
