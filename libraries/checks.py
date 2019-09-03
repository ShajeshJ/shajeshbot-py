import discord.ext.commands as cmd
from config import BOT_CH_ID, ADMIN_ID
from libraries.error import BotChannelError, AdminOnlyError

def is_bot_channel():
    async def predicate(ctx: cmd.Context):
        if ctx.channel.id != BOT_CH_ID:
            raise BotChannelError()
        return True
    return cmd.check(predicate)

def admin_only():
    async def predicate(ctx: cmd.Context):
        if ctx.author.id != ADMIN_ID:
            raise AdminOnlyError(f'{ctx.author} attempted to use the command {ctx.invoked_with}')
        return True
    return cmd.check(predicate)
