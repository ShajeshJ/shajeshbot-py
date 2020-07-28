import discord.ext.commands as cmd
import discord

class UsersCog(cmd.Cog, name='Users'):
    def __init__(self, bot):
        self.bot = bot


    @cmd.Cog.listener(name='on_member_update')
    async def fix_nicknames(self, before, after):
        if after.nick:
            new_nick = null
            identifier = f' [{after.name}]'

            if before.name != after.name:
                new_nick = null
            elif not after.nick.endswith(identifier):
                new_nick = f'{after.nick}{identifier}'
                if len(new_nick) > 32:
                    await before.send(f'Your new nickname cannot be longer than {32-len(identifier)} characters')
                    new_nick = before.nick
            else:
                return

            try:
                await after.edit(nick=new_nick)
            except discord.errors.Forbidden:
                print(f'Could not change nickname "{after.nick}" for {after}')
            except discord.errors.HTTPException as e:
                print(str(e))


def setup(bot):
    bot.add_cog(UsersCog(bot))
