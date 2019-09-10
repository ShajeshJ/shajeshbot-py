import random
import asyncio
import discord
import discord.ext.commands as cmd
from libraries.checks import is_bot_channel, admin_only
from utilities.parsing import parse_dice_args, extract_discord_msg_urls
from utilities.decorators import show_typing
from config import GUILD_ID, BOT_CH_ID

class MessagesCogs(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='dice')
    @is_bot_channel()
    @show_typing
    async def roll_dice(self, ctx, *, dice_args: str):
        dice_args = parse_dice_args(dice_args)

        min_val = dice_args['min']
        max_val = dice_args['max']
        offset = dice_args['offset']

        len_of_min = len(str(min_val))
        len_of_max = len(str(max_val))
        len_of_offset = len(str(abs(offset)))
        len_of_value = max(len_of_min, len_of_max)

        output = ""
        min_len = 19 + len_of_min + len_of_max + len_of_value + len_of_offset

        for i in range(dice_args['num_rolls']):
            rng_val = random.randint(min_val, max_val)

            if offset == 0:
                output = f'{output}Rolling ({min_val} - {max_val}): {rng_val}\n'
            elif offset > 0:
                line = f'Rolling ({min_val} - {max_val}): {rng_val} + {offset} '
                line = line.ljust(min_len)
                output = f'{output}{line}= {rng_val + offset}\n'
            else:
                line = f'Rolling ({min_val} - {max_val}): {rng_val} - {offset * -1} '
                line = line.ljust(min_len)
                output = f'{output}{line}= {rng_val + offset}\n'

        output = output.rstrip('\n')
        await ctx.send(f'```{output}```')

    @roll_dice.error
    async def dice_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'dice_args':
                await ctx.send('Must specify input parameters')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.Cog.listener(name='on_message')
    async def create_quoted_msgs(self, message):
        msg_urls = extract_discord_msg_urls(message.content)
        guild = None

        for msg_url in msg_urls:
            if msg_url['guild_id'] != GUILD_ID:
                continue

            guild = self.bot.get_guild(GUILD_ID) if not guild else guild
            channel = guild.get_channel(msg_url['channel_id'])
            if not channel or not isinstance(channel, discord.TextChannel):
                continue

            try:
                msg = await channel.fetch_message(msg_url['message_id'])
            except discord.NotFound:
                continue

            embed = discord.Embed()

            embed.set_author(
                name=msg.author.name,
                icon_url=msg.author.avatar_url
            )

            description = ''

            img_url = None
            if msg.attachments:
                url = msg.attachments[0].url
                if any(url.endswith(imgfmt) for imgfmt in [".gif", ".png", ".jpg"]):
                    img_url = url

            if not img_url:
                for msgEmbed in msg.embeds:
                    if msgEmbed.type == 'image':
                        img_url = msgEmbed.url
                        break

            if img_url:
                embed.set_image(url=img_url)

            if msg.content:
                description = f'{description}{msg.content}\n'

            if description:
                description = f'{description}\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_'

            embed.description = f'{description}\n[**View Original**]({msg_url["original"]})'
            embed.set_footer(text=f'in #{channel.name}')
            if msg.edited_at:
                embed.timestamp = msg.edited_at
            else:
                embed.timestamp = msg.created_at

            await message.channel.send('', embed=embed)

            # Only quote one at a time for now
            break


    @cmd.command(name='say')
    @admin_only()
    @cmd.dm_only()
    @show_typing
    async def make_bot_say(self, ctx, *, message: str):
        channel = self.bot.get_channel(BOT_CH_ID)
        if channel:
            await channel.send(message)

    @make_bot_say.error
    async def bot_say_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'message':
                await ctx.send('Must specify the message for the bot to say')
        else:
            await self.bot.handle_error(ctx, error)


    @cmd.command(name='rm')
    @admin_only()
    @cmd.guild_only()
    @show_typing
    async def delete_messages(self, ctx, num_msgs: int, supress_output = False):
        if ctx.guild.id != GUILD_ID:
            await ctx.send('The command can only be used in the Peanuts guild')
        elif num_msgs < 1 or num_msgs > 99:
            await ctx.send('Requested number of messages to delete must be between 1 to 99 inclusive.')
        else:
            tasks = []
            async for message in ctx.history(limit=num_msgs+1):
                tasks.append(asyncio.create_task(message.delete()))

            for task in tasks:
                await task

            if not supress_output:
                await ctx.send(f'{num_msgs} messages deleted successfully.')

    @delete_messages.error
    async def delete_msgs_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'num_msgs':
                await ctx.send('Must specify the number of messages to delete')
        else:
            await self.bot.handle_error(ctx, error)


def setup(bot):
    bot.add_cog(MessagesCogs(bot))
