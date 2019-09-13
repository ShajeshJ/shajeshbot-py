import re
import requests
from io import BytesIO

import discord
import discord.ext.commands as cmd

from libraries.checks import is_bot_channel, admin_only
from libraries.error import (
    BotChannelError,
    AdminOnlyError,
)
from libraries.decorators import show_typing
from config import ADMIN_ID, GUILD_ID, BOT_CH_ID

class EmojisCog(cmd.Cog, name='Emojis'):
    __pendingEmojis = {}

    def __init__(self, bot):
        self.bot = bot


    @cmd.command(
        name='emoji', aliases=['emote', 'ereq'],
        brief='Request an emoji', usage='<emoji_shortcut>'
    )
    @is_bot_channel()
    @show_typing
    async def request_emoji(self, ctx, *, shortcut: str):
        """
        This command will request a new guild emoji. The emoji shortcut can only contain 
        alphanumeric and underscore characters. You cannot specify a shortcut for an existing emoji.
        <\\n><\\n>
        The emoji image to use should be added as an attachment to the message. Only 1 image should 
        be attached, and the image cannot be any larger than 256 kb.
        <\\n><\\n>
        You can update the image of an actively pending emoji by using this command with the same shortcut 
        name as the pending request.
        <\\n><\\n>
        Once the request is created, you will be notified if it is denied by an admin.
        """

        shortcut = shortcut.lower()

        if not self._is_alphanumeric(shortcut):
            await ctx.send(
                f'"{shortcut}" is not a valid shortcut. '
                'Shortcuts can only contain alphanumeric and underscore characters.'
            )
            return

        if any(emoji.name.lower() == shortcut for emoji in ctx.guild.emojis):
            await ctx.send(f'"{shortcut}" has already been taken')
            return

        is_add_request = True

        if shortcut in self.__pendingEmojis.keys():
            if self.__pendingEmojis[shortcut]['user_id'] != ctx.author.id:
                await ctx.send(f'"{shortcut}" is an already pending shortcut')
                return
            else:
                is_add_request = False

        if len(ctx.message.attachments) != 1:
            await ctx.send('Must attach exactly 1 image to be uploaded as the emoji')
            return

        url = ctx.message.attachments[0].url

        self.__pendingEmojis[shortcut] = {
            'shortcut': shortcut,
            'url': url,
            'user': ctx.author
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
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'shortcut':
                await ctx.send('Must specify the shortcut to use')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.command(name='approveemoji', hidden=True)
    @admin_only()
    @cmd.dm_only()
    @show_typing
    async def approve_emoji(self, ctx, *, shortcut: str):
        if shortcut not in self.__pendingEmojis:
            await ctx.send(f'{shortcut} does not correspond to an active emoji request.')
            return

        guild = self.bot.get_guild(GUILD_ID)
        bot_channel = guild.get_channel(BOT_CH_ID)

        url = self.__pendingEmojis[shortcut]['url']
        user = self.__pendingEmojis[shortcut]['user']

        try:
            img_content = requests.get(url).content
            image = BytesIO(img_content).getvalue()
        except:
            await ctx.send(f'Failed to download the emoji image from {url}')
            await bot_channel.send(
                f'{user.mention} the emoji "{shortcut}" could not be approved'\
                ' because the image failed to download.'
            )
            return

        try:
            emoji = await guild.create_custom_emoji(name=shortcut, image=image)
        except discord.errors.HTTPException as e:
            print(f'HTTP Status: {e.status} - Error Code: {e.code} - Error Response: {e.text}')
            await ctx.send(f'Failed to uploaded the emoji image {url} because it\'s too large')
            await bot_channel.send(
                f'{user.mention} the emoji "{shortcut}" could not be uploaded'\
                f' because the image {url} is larger than 256 kb.'
            )
            return
        except discord.errors.InvalidArgument as e:
            print(str(e))
            await bot_channel.send(
                f'{user.mention} the emoji "{shortcut}" could not be approved'\
                f' because the uploaded file {url} was not a valid image'
            )
            return
        finally:
            del self.__pendingEmojis[shortcut]

        msg = await bot_channel.send(f'Emoji "{shortcut}" added successfully')
        await ctx.send('Emoji added successfully')
        await msg.add_reaction(emoji)

    @approve_emoji.error
    async def approve_emoji_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'shortcut':
                await ctx.send('Must specify the shortcut to add')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.command(name='rejectemoji', hidden=True)
    @admin_only()
    @cmd.dm_only()
    @show_typing
    async def reject_emoji(self, ctx, shortcut: str, *, reason:str):
        if shortcut not in self.__pendingEmojis:
            await ctx.send(f'{shortcut} does not correspond to an active emoji request.')
            return

        guild = self.bot.get_guild(GUILD_ID)
        bot_channel = guild.get_channel(BOT_CH_ID)

        url = self.__pendingEmojis[shortcut]['url']
        user = self.__pendingEmojis[shortcut]['user']

        del self.__pendingEmojis[shortcut]

        embed = discord.Embed(title='Reason', description=reason)
        await bot_channel.send(content=f'{user.mention} your emoji "{shortcut}" was rejected {url}', embed=embed)
        await ctx.send('Emoji rejected successfully')

    @reject_emoji.error
    async def reject_emoji_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'shortcut':
                await ctx.send('Must specify the shortcut to reject')
            elif error.param.name == 'reason':
                await ctx.send('Must specify a reason to reject the shortcut')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.command(name='listemojis', hidden=True)
    @admin_only()
    @cmd.dm_only()
    @show_typing
    async def list_emojis(self, ctx):
        if len(self.__pendingEmojis) == 0:
            await ctx.send('There are no currently pending emojis')
        else:
            for k, v in self.__pendingEmojis.items():
                await ctx.send(f'{v["shortcut"]}: {v["url"]}')


    @staticmethod
    def _is_alphanumeric(string: str):
        return re.fullmatch('[a-zA-Z0-9_]+', string)


def setup(bot):
    bot.add_cog(EmojisCog(bot))
