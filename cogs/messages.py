import random
import asyncio
import discord
import discord.ext.commands as cmd
from libraries.checks import is_bot_channel, admin_only
from libraries.parsing import parse_dice_args, extract_discord_msg_urls
from libraries.decorators import show_typing
from libraries.converters import CommandConverter
from config import GUILD_ID, BOT_CH_ID

class MessagesCogs(cmd.Cog, name='Messages'):
    ZW_SPACE = '\u200b'

    def __init__(self, bot):
        self.bot = bot


    @cmd.command(
        name='dice', aliases=['rng', 'roll', 'random'], brief='Generate random numbers',
        usage='{ <dice_notation> |OR| <num> [num] [num] }'
    )
    @is_bot_channel()
    @show_typing
    async def roll_dice(self, ctx, *, dice_args: str):
        """
        Use this command to generate a set of random numbers within a certain bounds. This 
        command can be used in one of two ways.
        <\\n><\\n>
        1) You can specify dice notation for the input. Dice notation is "#d#[+/-]#". For 
        example, "3d20-4". This would essentially roll 3 dice with 20 sides, and subtract 
        4 from the output.
        <\\n><\\n>
        2) You can also specify anywhere from 1 to 3 space separated numbers. The behaviour 
        for set of numbers is as follows:<\\n><\\n>
            **- 1 number**: 1 random number is generated with 1 and your input as the min/max bounds. 
            For example, `!dice 20` will generate a random number from 1 to 20.<\\n><\\n>
            **- 2 numbers**: 1 random number is generated, with your 1st/2nd inputs as the min/max bound. 
            For example, `!dice -5 15` will generate a random number from -5 to 15.<\\n><\\n>
            **- 3 numbers**: Your 1st/2nd inputs specify the min/max bounds, and your 3rd number specifies the
            amount of numbers to generate. For example, `!dice 13 45 5` will generate 5 random numbers 
            from 13 to 45.
        """

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


    @cmd.command(name='say', hidden=True)
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


    @cmd.command(name='rm', hidden=True)
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


    @cmd.command(
        name='help', aliases=['info', 'h'],
        brief='Shows help usage for commands', usage='[command_name]'
    )
    @is_bot_channel()
    @show_typing
    async def get_help(self, ctx, *, command: CommandConverter = None):
        """
        If the command name is not specified, then it will display a brief usage for all commands. 
        If a command is specified, then detailed usage will be shown for that specific command.
        <\\n><\\n>
        The command can be specified using the main name, or any of its aliases. This 
        parameter is also case-sensitive, and should not be prefixed with a command prefix.
        """

        if command:
            if command.hidden:
                return
            embed = await self.__construct_specific_help(ctx, command)
        else:
            embed = await self.__construct_general_help(ctx)

        await ctx.send('', embed=embed)

    async def __construct_general_help(self, ctx):
        prefix = ctx.bot.command_prefix

        embed = discord.Embed()
        embed.title = 'For detailed help use'
        embed.description = f'**```asciidoc\n=== {prefix}help <command> ===```**\n{self.ZW_SPACE}'
        embed.colour = 0x3473d9

        for cog_name, cog in ctx.bot.cogs.items():
            cmd_list = cog.get_commands()
            cmd_str = '\n'.join(
                f'{prefix}{command.name} - {command.brief}'
                for command in cmd_list
                if not command.hidden
            )

            if cmd_str:
                cmd_str = f'```{cmd_str}```'
                embed.add_field(name=f'**{cog_name.upper()}**', value=cmd_str, inline=False)

        return embed

    async def __construct_specific_help(self, ctx, command: cmd.Command):
        prefix = ctx.bot.command_prefix

        embed = discord.Embed()
        # embed.title = command.cog_name
        embed.description = f'**```asciidoc\n=== {prefix}{command.name} {command.usage} ===```**'
        embed.description += f' *<params> are required, and [params] are optional*\n{self.ZW_SPACE}'
        embed.colour = 0x3473d9

        embed.add_field(name='Short Description', value=command.brief)

        if command.aliases:
            embed.add_field(name='Aliases', value='\n'.join(prefix + alias for alias in command.aliases))

        details = command.help.replace('\n', '').replace('<\\n>', '\n')
        embed.add_field(name='Details', value=details, inline=False)

        return embed


def setup(bot):
    bot.add_cog(MessagesCogs(bot))
