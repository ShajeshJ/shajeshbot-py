import discord.ext.commands as cmd

class CommandConverter(cmd.Converter):
    async def convert(self, ctx: cmd.Context, argument):
        command = ctx.bot.get_command(argument)
        if command:
            return command
        else:
            raise cmd.BadArgument(f'"{argument}" is not an existing command')
