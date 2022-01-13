import discord
import os
import discord.ext
from discord.ext import commands, tasks
from dotenv import load_dotenv
from itertools import cycle
from os import listdir
from pathlib import Path


"""
Loading token from .env,
loading cogs (modules),
and making a cool status updator.
"""

load_dotenv()
client = discord.Client()
client = commands.Bot(command_prefix='mega')

if not Path("badlinks.json").is_file():
    f = open("badlinks.json", "w")
    f.write("{}")
    f.close()

@client.event
async def on_ready():
    print("bot online")
    change_status.start()


@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


# awesome status list to cycle from
statuslist = cycle([
    'with caution',
    'with rad security measures',
])


@tasks.loop(seconds=60)  # 60 to stay on discord's good list
async def change_status():
    await client.change_presence(activity=discord.Game(next(statuslist)))


"""
Initialize Cogs (modules) and run bot
"""

for cog in listdir('./cogs'):
    if cog.endswith('.py') == True:
        client.load_extension(f'cogs.{cog[:-3]}')

client.run(os.getenv("TOKEN"))
