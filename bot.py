from discord.ext.commands import (
    Bot,
    has_permissions,
    MissingPermissions,
)
import discord
from config import BOT_TOKEN
from error import missing_perms_template

class ShajeshBot(Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

bot = ShajeshBot(command_prefix='!')


@bot.command('reloadext', hidden=True)
@has_permissions(administrator=True)
async def reload_ext(ctx, *, ext:str):

    async def try_reload(ext, send_error=False):
        try:
            bot.reload_extension(ext)
        except:
            if send_error:
                print(f'**ERROR** {type(e).__name__} - {e}')
                await ctx.send('fail')
            return False
        else:
            print(f'Reloaded {ext}')
            await ctx.send('success')
            return True

    if await try_reload(ext):
        return

    await try_reload('cogs.' + ext, True)


@reload_ext.error
async def reload_ext_error_handler(ctx, error):
    if isinstance(error, MissingPermissions):
        print(missing_perms_template('reload extension', ctx, error))
    else:
        raise error


bot.load_extension('cogs.roles')
bot.load_extension('cogs.emojis')

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
