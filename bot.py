from discord.ext.commands import (
    Bot,
    has_permissions,
    MissingPermissions,
)
import discord
from config import BOT_TOKEN
from error_templates import missing_perms_template

class ShajeshBot(Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

bot = ShajeshBot(command_prefix='!')


@bot.command('reloadext', hidden=True)
@has_permissions(administrator=True)
async def reload_ext(ctx, *, ext:str):
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

@reload_ext.error
async def reload_ext_error_handler(ctx, error):
    if isinstance(error, MissingPermissions):
        print(missing_perms_template('reload extension', ctx, error))
    else:
        raise error


bot.load_extension('cogs.roles')

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
