import discord.ext.commands as cmd
import discord

from libraries.checks import is_bot_channel
from libraries.decorators import show_typing
from libraries.stocks_api import StocksApiWrapper

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from io import BytesIO

class StocksCog(cmd.Cog, name='Stocks'):
    def __init__(self, bot):
        self.bot = bot


    @cmd.command(
        name='stock', aliases=['stocks'],
        brief='Get stock information', usage='<ticker>'
    )
    @is_bot_channel()
    @show_typing
    async def request_channel(self, ctx, ticker: str):
        """
        This command will retrieve daily stock information for the specified security.
        <\\n><\\n>
        The given ticker symbol must be valid; otherwise an error will be returned.
        <\\n><\\n>
        In addition, this command can only be used 5 times in a minute. If that limit is exceeded,
        an error will be returned instead.
        """

        api = StocksApiWrapper(ticker)
        resp = await api.get_daily()

        if resp is None:
            await ctx.send(f'No recent stock information for "{ticker.upper()}" available.')
            return

        embed = discord.Embed()
        embed.title = f'__{resp["symbol"]}__ Stock Info (Daily)'
        embed.url = f'https://ca.finance.yahoo.com/quote/{resp["symbol"]}'
        embed.colour = 0x8934d9
        embed.set_footer(text=f'Last refreshed {resp["refreshed"].date()}')

        if len(resp['datapoints']) < 2):
            today_dp = resp['datapoints'][-1]
            embed.description = f'**```diff\nData for yesterady unavailable```**'
            embed.add_field(name='Close', value=f'{today_dp["close"] : .2f}')
            embed.add_field(name='Open', value=f'{today_dp["open"] : .2f}')
            embed.add_field(name='Day\'s Range', value=f'{today_dp["low"]:.2f} - {today_dp["high"]:.2f}')
            await ctx.send('', embed=embed)
        else:
            today_dp = resp['datapoints'][-1]
            yest_dp = resp['datapoints'][-2]

            diff = today_dp['close'] - yest_dp['close']
            percent_diff = diff / yest_dp['close'] * 100

            sign = '' if diff < 0 else '+'
            embed.description = f'**```diff\n{sign}{diff:.2f} ({sign}{percent_diff:.2f}%)```**'

            embed.add_field(name='Close', value=f'{today_dp["close"] : .2f}')
            embed.add_field(name='Previous Close', value=f'{yest_dp["close"] : .2f}')
            embed.add_field(name='Open', value=f'{today_dp["open"] : .2f}')
            embed.add_field(name='Day\'s Range', value=f'{today_dp["low"]:.2f} - {today_dp["high"]:.2f}')

            plt.figure(figsize=(15,10), dpi=40)

            x = [d['date'] for d in resp['datapoints']]
            y = [d['close'] for d in resp['datapoints']]
            plt.plot(x, y, color='tab:red')

            plt.xticks(fontsize=24)
            plt.yticks(fontsize=24)

            plt.grid(axis='both', alpha=1)
            plt.gca().spines["top"].set_alpha(0.0)
            plt.gca().spines["bottom"].set_alpha(0.0)
            plt.gca().spines["right"].set_alpha(0.0)
            plt.gca().spines["left"].set_alpha(0.0)

            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)

            plt.close('all')

            embed.set_image(url='attachment://stocksgraph.png')
            await ctx.send(file=discord.File(img_buffer, 'stocksgraph.png'), embed=embed)


    @request_channel.error
    async def channel_error_handler(self, ctx, error):
        if isinstance(error, cmd.MissingRequiredArgument):
            if error.param.name == 'ticker':
                await ctx.send('Must specify the ticker symbol')
        else:
            await self.bot.handle_error(ctx, error)


def setup(bot):
    bot.add_cog(StocksCog(bot))
