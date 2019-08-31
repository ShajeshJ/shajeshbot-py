import os
from discord.ext.commands import Bot
from cogs.roles import RolesCog

class ShajeshBot(Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')


bot = ShajeshBot(command_prefix='!')
bot.add_cog(RolesCog(bot))

if __name__ == "__main__":
    bot.run(os.getenv('SHAJESHBOT_TOKEN'))
