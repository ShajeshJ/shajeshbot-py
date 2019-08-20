import discord
import os

class ShajeshBot(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


client = ShajeshBot()
client.run(os.getenv('SHAJESHBOT_TOKEN'))
