import re
import discord.ext.commands as cmd

# Try to match "{num}d{num}{+/-}{num}", such as 3d10+2
dice_regex = (
    ' *(?P<num_dice>\\d*) *d'
    ' *(?P<dice_size>\\d+) *'
    '('
    '(?P<offset_dir>\\+|-) *'
    '(?P<offset>\\d+) *'
    ')?'
)

# Try to match discord message link
discord_msg_url_regex = (
    'https?:\\/\\/discord\\.com\\/channels\\/'
    '(?P<g_id>[0-9]+)\\/'
    '(?P<c_id>[0-9]+)\\/'
    '(?P<m_id>[0-9]+)'
)


def parse_dice_args(argument) -> dict:
    dice_args = {}

    droll_notation = re.fullmatch(dice_regex, argument, re.IGNORECASE)
    if droll_notation:
        try:
            num_dice = droll_notation.group('num_dice')
            num_dice = int(num_dice) if num_dice != '' else 1

            size = int(droll_notation.group('dice_size'))

            offset = droll_notation.group('offset')
            if offset:
                offset_dir = droll_notation.group('offset_dir')
                offset = int(offset) if offset_dir == '+' else int(offset) * -1
            else:
                offset = 0

            dice_args = {
                'min': 1,
                'max': size,
                'num_rolls': num_dice,
                'offset': offset
            }
        except:
            raise cmd.BadArgument(f'Failed to parse "{argument}" in dice notation')
    else:
        try:
            args = [int(a) for a in argument.split(' ')]
        except:
            raise cmd.BadArgument(f'Must specify dice notation or space-separated integer parameters only')

        num_args = len(args)

        min_val, max_val, num_rolls = (0, 0, 0)
        if num_args == 0:
            raise cmd.BadArgument(f'Must specify input parameters')
        elif num_args == 1:
            min_val, max_val, num_rolls = (1, args[0], 1)
        elif num_args == 2:
            min_val, max_val, num_rolls = (args[0], args[1], 1)
        elif num_args == 3:
            min_val, max_val, num_rolls = (args[0], args[1], args[2])
        else:
            raise cmd.BadArgument(f'Can only accept up to 3 integer parameters')

        dice_args = {
            'min': min_val,
            'max': max_val,
            'num_rolls': num_rolls,
            'offset': 0
        }

    if dice_args['num_rolls'] < 1:
        raise cmd.BadArgument(f'Number of rolls cannot be less than 1')
    elif dice_args['max'] < dice_args['min']:
        raise cmd.BadArgument(
            f'The max value ({dice_args["max"]}) must be greater than '
            f'or equal to the min value ({dice_args["min"]})'
        )

    return dice_args


def extract_discord_msg_urls(content: str):
    msg_urls = []
    for url in re.finditer(discord_msg_url_regex, content):
        msg_urls.append({
            'guild_id': int(url.group('g_id')),
            'channel_id': int(url.group('c_id')),
            'message_id': int(url.group('m_id')),
            'original': url.group(0)
        })
    return msg_urls
