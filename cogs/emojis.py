import discord
import discord.ext.commands as cmd

class EmojisCog(cmd.Cog, name='Emoji'):
    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='emoji')
    async def request_emoji(self, ctx: cmd.Context, *, role_name: str):
        pass


def setup(bot):
    bot.add_cog(EmojisCog(bot))
