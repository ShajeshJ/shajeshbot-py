import discord.ext.commands as cmd

class UnexpectedDataError(cmd.CommandError):
    pass

class BotChannelError(cmd.CommandError):
    pass

class AdminOnlyError(cmd.CommandError):
    pass

def missing_perms_template(cmd, ctx, error):
    return (
        f'{ctx.message.author} failed to run {cmd}. '
        f'Missing permissions: {", ".join(error.missing_perms)}'
    )
