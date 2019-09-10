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
    BotChannelError
)

class ShajeshBot(Bot):
    __common_errors = (
        BotChannelError,
        PrivateMessageOnly,
        AdminOnlyError,
        BadArgument
    )


    async def on_ready(self):
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


    async def __handle_common_errors(self, context, exception):
        if isinstance(exception, BotChannelError):
            pass
        elif isinstance(exception, PrivateMessageOnly):
            pass
        elif isinstance(exception, AdminOnlyError):
            print(str(exception))
        elif isinstance(exception, BadArgument):
            await context.send(str(exception))
