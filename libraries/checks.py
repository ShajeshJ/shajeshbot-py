import discord.ext.commands as cmd
from config import BOT_CH_ID, ADMIN_ID

def is_bot_channel():
    async def predicate(ctx: cmd.Context):
        return ctx.channel.id == BOT_CH_ID
    return cmd.check(predicate)

def admin_only():
    async def predicate(ctx: cmd.Context):
        return ctx.author.id == ADMIN_ID
    return cmd.check(predicate)
