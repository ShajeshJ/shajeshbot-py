import discord.ext.commands as cmd

class UnexpectedDataError(cmd.CommandError):
    pass

class BotChannelError(cmd.CommandError):
    pass

class AdminOnlyError(cmd.CommandError):
    pass

class StocksApiError(cmd.CommandError):
    pass
