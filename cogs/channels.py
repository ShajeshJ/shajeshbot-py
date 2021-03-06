import discord.ext.commands as cmd
import discord
import re

from libraries.checks import is_bot_channel, admin_only
from libraries.decorators import show_typing
from config import ADMIN_ID, BOT_CH_ID, GUILD_ID

class ChannelsCog(cmd.Cog, name='Channels'):
    __pendingChs = {}

    def __init__(self, bot):
        self.bot = bot


    @cmd.command(
        name='channel', aliases=['creq'],
        brief='Request a channel', usage='<channel> [category]'
    )
    @is_bot_channel()
    @show_typing
    async def request_channel(self, ctx, channel: str, *,
            category: discord.CategoryChannel = None):
        """
        This command will request a new text channel. The channel name can only contain 
        alphanumeric, dash, and underscore characters. You cannot specify a name for an 
        existing or pending channel.
        <\\n><\\n>
        You can optionally specify an existing category for the text channel. The category 
        name is case sensitive.
        <\\n><\\n>
        Once the request is created, you will be notified when it is approved or denied by 
        an admin.
        """

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
            'name': channel,
            'user': ctx.author
        }

        msg_to_send = f'{ctx.author} requested a text channel "{channel}"'
        if category:
            msg_to_send = msg_to_send + f' in the {category.name} category'

        admin = ctx.guild.get_member(ADMIN_ID)
        await admin.send(msg_to_send)
        await ctx.send('Channel request sent successfully')

    @request_channel.error
    async def channel_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'channel':
                await ctx.send('Must specify the channel name')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.command(name='approvechannel', hidden=True)
    @admin_only()
    @cmd.dm_only()
    @show_typing
    async def approve_channel(self, ctx, channel:str):
        if channel not in self.__pendingChs.keys():
            await ctx.send(f'{channel} is not an active channel request')
            return

        guild = self.bot.get_guild(GUILD_ID)
        category = self.__pendingChs[channel]['category']
        user = self.__pendingChs[channel]['user']

        text_ch = await guild.create_text_channel(channel, category=category)

        del self.__pendingChs[channel]

        await text_ch.send(f'{user.mention} your requested channel has been created.')
        await ctx.send('Channel added successfully')

    @approve_channel.error
    async def approve_channel_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'channel':
                await ctx.send('Must specify the channel to approve')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.command(name='rejectchannel', hidden=True)
    @admin_only()
    @cmd.dm_only()
    @show_typing
    async def reject_channel(self, ctx, channel:str, *, reason:str):
        if channel not in self.__pendingChs.keys():
            await ctx.send(f'{channel} is not an active channel request')
            return

        guild = self.bot.get_guild(GUILD_ID)
        bot_channel = guild.get_channel(BOT_CH_ID)

        user = self.__pendingChs[channel]['user']

        del self.__pendingChs[channel]

        embed = discord.Embed(title='Reason', description=reason)
        await bot_channel.send(content=f'{user.mention} your channel "{channel}" was rejected', embed=embed)
        await ctx.send('Channel rejected successfully')

    @reject_channel.error
    async def reject_channel_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'channel':
                await ctx.send('Must specify the channel to reject')
            elif error.param.name == 'reason':
                await ctx.send('Must specify a reason to reject the channel')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.command(name='listchannels', hidden=True)
    @admin_only()
    @cmd.dm_only()
    @show_typing
    async def list_channels(self, ctx):
        if len(self.__pendingChs) == 0:
            await ctx.send('There are no currently pending channels')
        else:
            for k, v in self.__pendingChs.items():
                msg_to_send = f'{k}: {v["category"] if v["category"] else "N/A"}'
                await ctx.send(msg_to_send)


    @staticmethod
    def _valid_channel_name(string: str):
        return re.fullmatch('[a-zA-Z0-9_\\-]+', string)


def setup(bot):
    bot.add_cog(ChannelsCog(bot))
