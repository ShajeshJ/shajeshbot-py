from discord.ext.commands import Bot
from config import BOT_TOKEN

class ShajeshBot(Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

bot = ShajeshBot(command_prefix='!')

@bot.command('reloadext', hidden=True)
async def cog_ext(ctx, *, ext:str):
    try:
        bot.reload_extension(ext)
    except Exception as e:
        print(f'**ERROR** {type(e).__name__} - {e}')
        print("Loaded Cogs: ")
        for loaded_ext in bot.extensions:
            print(loaded_ext)
        await ctx.send('fail')
    else:
        print(f'Reloaded {ext}')
        await ctx.send('success')


bot.load_extension('cogs.roles')

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
