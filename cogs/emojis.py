from typing import Optional
import re
from urllib.request import urlopen

import discord
import discord.ext.commands as cmd

from libraries.checks import is_bot_channel, admin_only
from libraries.error import BotChannelError, AdminOnlyError
from config import ADMIN_ID, GUILD_ID, BOT_CH_ID

class EmojisCog(cmd.Cog, name='Emoji'):
    __pendingEmojis = {}

    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='emoji')
    @is_bot_channel()
    async def request_emoji(self, ctx, *, shortcut: str):
        if not self._is_alphanumeric(shortcut):
            await ctx.send(
                f'"{shortcut}" is not a valid shortcut. '
                'Shortcuts can only contain alphanumeric and underscore characters.'
            )
            return

        if any(emoji.name == shortcut for emoji in ctx.guild.emojis):
            await ctx.send(f'"{shortcut}" has already been taken')
            return

        is_add_request = True

        if shortcut in self.__pendingEmojis:
            if self.__pendingEmojis[shortcut]['user_id'] != ctx.author.id:
                await ctx.send(f'"{shortcut}" is an already pending shortcut')
                return
            else:
                is_add_request = False

        if len(ctx.message.attachments) != 1:
            await ctx.send('Must attach exactly 1 image to be uploaded as the emoji')
            return

        url = ctx.message.attachments[0].url
        user_id = ctx.author.id

        self.__pendingEmojis[shortcut] = {
            'shortcut': shortcut,
            'url': url,
            'user_id': user_id
        }

        admin = ctx.guild.get_member(ADMIN_ID)
        if is_add_request:
            await admin.send(f'{ctx.author} requested to add the emoji {url} with shortcut "{shortcut}"')
            await ctx.send(f'Emoji request for "{shortcut}" sent successfully')
        else:
            await admin.send(f'{ctx.author} updated emoji request for "{shortcut}" with {url}')
            await ctx.send(f'Emoji request for "{shortcut}" updated successfully')

    @request_emoji.error
    async def emoji_error_handler(self, ctx, error):
        if isinstance(error, cmd.BadArgument):
            await ctx.send(str(error))
        elif isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'shortcut':
                await ctx.send('Must specify the shortcut to add')
        elif isinstance(error, BotChannelError):
            pass
        else:
            raise error


    @cmd.command(name='acceptemoji')
    @admin_only()
    @cmd.dm_only()
    async def approve_emoji(self, ctx, *, shortcut: str):
        if shortcut not in self.__pendingEmojis:
            await ctx.send(f'{shortcut} does not correspond to an active emoji request.')
            return

        guild = self.bot.get_guild(GUILD_ID)

        emoji_request = self.__pendingEmojis[shortcut]
        url = emoji_request['url']
        user_id = emoji_request['user_id']

        try:
            with urlopen(url) as conn:
                image = conn.read()
        except:
            await ctx.send(f'Failed to download the emoji image from {url}')
            return

        emoji = await guild.create_custom_emoji(shortcut, image)
        del self.__pendingEmojis[shortcut]

        bot_channel = guild.get_channel(BOT_CH_ID)

        msg = await bot_channel.send(f'Emoji {shortcut} added successfully')
        await msg.add_reaction(emoji)

    @approve_emoji.error
    async def approve_emoji_error_handler(self, ctx, error):
        if isinstance(error, cmd.BadArgument):
            await ctx.send(str(error))
        elif isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'shortcut':
                await ctx.send('Must specify the shortcut to add')
        elif isinstance(error, AdminOnlyError):
            print(str(error))
        elif isinstance(error, cmd.PrivateMessageOnly):
            pass
        else:
            raise error


    @cmd.command(name='rejectemoji')
    @admin_only()
    @cmd.dm_only()
    async def reject_emoji(self, ctx, shortcut: str, *, reason:str):
        if shortcut not in self.__pendingEmojis:
            await ctx.send(f'{shortcut} does not correspond to an active emoji request.')
            return

        guild = self.bot.get_guild(GUILD_ID)

        url = self.__pendingEmojis[shortcut]['url']
        user_id = self.__pendingEmojis[shortcut]['user_id']

        del self.__pendingEmojis[shortcut]

        user = guild.get_member(user_id)
        bot_channel: discord.TextChannel = guild.get_channel(BOT_CH_ID)
        embed = discord.Embed(title='Reason', description=reason)

        await bot_channel.send(content=f'{user.mention} your emoji {shortcut} was rejected {url}', embed=embed)

    @reject_emoji.error
    async def reject_emoji_error_handler(self, ctx, error):
        if isinstance(error, cmd.BadArgument):
            await ctx.send(str(error))
        elif isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'shortcut':
                await ctx.send('Must specify the shortcut to reject')
            elif error.param.name == 'reason':
                await ctx.send('Must specify a reason to reject the shortcut')
        elif isinstance(error, AdminOnlyError):
            print(str(error))
        elif isinstance(error, cmd.PrivateMessageOnly):
            pass
        else:
            raise error


    @cmd.command(name='listemojis')
    @admin_only()
    @cmd.dm_only()
    async def list_emojis(self, ctx):
        if len(self.__pendingEmojis) == 0:
            await ctx.send('There are no currently pending emojis')
        else:
            for k, v in self.__pendingEmojis.items():
                await ctx.send(f'{v["shortcut"]}: {v["url"]}')

    @list_emojis.error
    async def list_emojis_error_handler(self, ctx, error):
        if isinstance(error, AdminOnlyError):
            print(str(error))
        elif isinstance(error, cmd.PrivateMessageOnly):
            pass
        else:
            raise error


    @staticmethod
    def _is_alphanumeric(string: str):
        return re.fullmatch('[a-zA-Z0-9_]+', string)


def setup(bot):
    bot.add_cog(EmojisCog(bot))
