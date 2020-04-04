import traceback
import sys
import discord
from discord.ext.commands import (
    Bot,
    PrivateMessageOnly,
    BadArgument
)

from libraries.error import (
    AdminOnlyError,
    BotChannelError,
    StocksApiError,
)

class ShajeshBot(Bot):
    __common_errors = (
        BotChannelError,
        PrivateMessageOnly,
        AdminOnlyError,
        BadArgument,
        StocksApiError,
    )


    async def on_ready(self):
        # status = discord.CustomActivity(name='Message "!help" for commands')
        status = discord.Activity(type=discord.ActivityType.watching, name="for !help command")
        await self.change_presence(activity=status)
        print(f'Logged on as {self.user}')


    # Is called for ALL commands, regardless of if there is a local exception handler
    async def on_command_error(self, context, exception):
        if isinstance(exception, self.__common_errors):
            await self.__handle_common_errors(context, exception)
        else:
            await super().on_command_error(context, exception)


    # Function that we should call as last resort in local exception handlers
    async def handle_error(self, context, exception):
        if not isinstance(exception, self.__common_errors):
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
            await context.send('Something seriously broke... send help...')


    async def __handle_common_errors(self, context, exception):
        if isinstance(exception, BotChannelError):
            pass
        elif isinstance(exception, PrivateMessageOnly):
            pass
        elif isinstance(exception, AdminOnlyError):
            print(str(exception))
        elif isinstance(exception, BadArgument):
            await context.send(str(exception))
        elif isinstance(exception, StocksApiError):
            if exception.__cause__ is not None:
                cause = exception.__cause__
                traceback.print_exception(type(cause), cause, cause.__traceback__, file=sys.stderr)
            await context.send(str(exception))
