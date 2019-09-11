from functools import wraps
from discord.ext.commands import Context

# Every cog command should pass the cog (self) as first arg, and ctx as second
def show_typing(coro):
    @wraps(coro)
    async def wrapper(self, ctx, *args, **kwargs):
        if isinstance(ctx, Context):
            async with ctx.typing():
                return await coro(self, ctx, *args, **kwargs)
        else:
            raise TypeError(
                'This decorator can only be used with cog commands, '
                'where the second argument is the context.'
            )
    return wrapper
