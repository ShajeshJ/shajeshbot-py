from config import (
    STOCKS_API_KEY as API_KEY,
    STOCKS_API_BASE_URL as BASE_URL
)
from aiohttp import ClientSession
import discord.ext.commands as cmd
from datetime import datetime
from pytz import timezone
from libraries.error import StocksApiError


class StocksApiWrapper:
    __FUNC = {
        "daily": "TIME_SERIES_DAILY_ADJUSTED"
    }

    def __init__(self, ticker: str):
        self.ticker = ticker

    async def get_daily(self):
        data = await self.__make_request(self.__FUNC['daily'])

        if not data:
            return None

        try:
            meta_data = data['Meta Data']
            datapoints = data['Time Series (Daily)']

            resp = {}

            resp['symbol'] = self.ticker.upper()
            resp['refreshed'] = datetime.fromisoformat(meta_data['3. Last Refreshed'])
            resp['refreshed'] = timezone(meta_data['5. Time Zone']).localize(resp['refreshed'])

            resp['datapoints'] = [{
                'date': datetime.fromisoformat(k),
                'open': float(v['1. open']),
                'high': float(v['2. high']),
                'low': float(v['3. low']),
                'close': float(v['4. close']),
                'volume': float(v['6. volume']),
            } for k, v in datapoints.items()]

            resp['datapoints'].sort(key=lambda d: d['date'])
        except Exception as e:
            raise StocksApiError('An unexpected error occurred') from e

        return resp


    async def __make_request(self, api_func: str):
        """
        Query stocks API using the `api_func` function
        """

        params = {
            "function": api_func,
            "symbol": self.ticker,
            "apikey": API_KEY
        }
        try:
            async with ClientSession() as session:
                async with session.get(BASE_URL, params=params) as resp:
                    data = await resp.json()
        except Exception as e:
            raise StocksApiError('An unexpected error occurred') from e

        """
        Everything just comes back as a 200 with no response headers convention.
        Unfortunately, the only way to detect any potential errors is to just 
        arbitrarily check for parameters and hope it contains the expected information
        """
        if 'Note' in data:
            print(f'Stocks API error body for {self.ticker} using function {api_func}: {data}')
            raise StocksApiError('The 5 calls per minute API limit has been hit. Try again in a minute')

        if 'Error Message' in data:
            print(f'Stocks API error body for {self.ticker} using function {api_func}: {data}')
            raise StocksApiError(f'"{self.ticker}" is not a valid ticker symbol')

        return data
