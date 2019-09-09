import random
import discord.ext.commands as cmd
from libraries.checks import is_bot_channel
from utilities.dice_parsing import parse_dice_args

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


def setup(bot):
    bot.add_cog(MessagesCogs(bot))
