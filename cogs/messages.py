import random
import discord
import discord.ext.commands as cmd
from libraries.checks import is_bot_channel
from utilities.parsing import parse_dice_args, extract_discord_msg_urls
from config import GUILD_ID

class MessagesCogs(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cmd.command(name='dice')
    @is_bot_channel()
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

            if msg.attachments:
                img = str(msg.attachments[0].url)
                if any(img.endswith(imgfmt) for imgfmt in ["gif", "png", "jpg"]):
                    embed.set_image(img)

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


def setup(bot):
    bot.add_cog(MessagesCogs(bot))
