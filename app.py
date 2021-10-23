import discord
from bot import ShajeshBot
from config import BOT_TOKEN
from libraries.checks import admin_only
import os
import traceback

bot = ShajeshBot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')

unloaded_files = []
for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
        except:
            unloaded_files.append(filename)
            traceback.print_exc()
if unloaded_files:
    print(f'Failed to load the following extension files: {", ".join(unloaded_files)}')


@bot.command('reloadext', hidden=True)
@admin_only()
async def reload_ext(ctx, *, ext:str):
    async def try_reload(ext, send_error=False):
        try:
            bot.reload_extension(ext)
        except Exception as e:
            if send_error:
                print(f'**ERROR** {type(e).__name__} - {e}')
                await ctx.send('fail')
            return False
        else:
            print(f'Reloaded {ext}')
            await ctx.send('success')
            return True

    if not await try_reload(ext):
        await try_reload('cogs.' + ext, True)


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
