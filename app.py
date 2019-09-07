from bot import ShajeshBot
from config import BOT_TOKEN
from libraries.checks import admin_only

#invite https://discordapp.com/oauth2/authorize?client_id=421836036101111818&scope=bot&permissions=1610087545

bot = ShajeshBot(command_prefix='!')
bot.load_extension('cogs.roles')
bot.load_extension('cogs.emojis')


@bot.command('reloadext', hidden=True)
@admin_only()
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

    if not await try_reload(ext):
        await try_reload('cogs.' + ext, True)


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
