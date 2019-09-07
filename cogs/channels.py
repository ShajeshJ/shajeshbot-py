import discord.ext.commands as cmd
import discord
from typing import Optional

from libraries.checks import is_bot_channel
from config import ADMIN_ID, BOT_CH_ID

class ChannelsCog(cmd.Cog):
    __pendingChs = {}

    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='channel')
    @is_bot_channel()
    async def request_channel(self, ctx, channel: str,
            *, category: Optional[discord.CategoryChannel]):
        name = channel
        channel = channel.lower()

        if not self._valid_channel_name(channel):
            await ctx.send(
                f'"{channel}" is not a valid channel name. '
                'Channels can only contain alphanumeric, dash, and underscore characters.'
            )
            return

        if any(ch.name.lower() == channel.lower() for ch in ctx.guild.channels):
            await ctx.send(f'"{channel}" is already an existing channel')
            return

        if channel in self.__pendingChs.keys():
            await ctx.send(f'"{channel}" is a currently pending channel')
            return

        self.__pendingChs[channel] = {
            'category': category,
            'name': name,
            'user': ctx.author
        }

        msg_to_send = f'{ctx.author} requested a text channel "{name}"'
        if not category:
            msg_to_send = msg_to_send + f' in the {category.name} category'

        admin = ctx.guild.get_member(ADMIN_ID)
        await admin.send(msg_to_send)
        await ctx.send('Channel request sent successfully')

    @request_channel.error
    async def channel_error_handler(self, ctx, error):
        if isinstance(error, cmd.BadArgument):
            await ctx.send(str(error))
        elif isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'channel':
                await ctx.send('Must specify the channel name')
        else:
            await self.bot.handle_error(error)


    @staticmethod
    def _valid_channel_name(string: str):
        return re.fullmatch('[a-zA-Z0-9_\\-]+', string)