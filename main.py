import discord
import os
import time
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check
import joblib
import sklearn
from utils import parse_url
import re
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()
pipeline = joblib.load('phishing.pkl')
client = commands.Bot(command_prefix='mega')


@client.event
async def on_ready():
    global logging_channel
    logging_channel = client.get_channel(849427163153563708)
    print("bot online")


@client.command()
async def predict(ctx, *, args):
    result = "safe" if pipeline.predict([parse_url(args)
                                         ])[0] != "bad" else "not safe"
    await ctx.reply(f"Predicted `{result}`")


@client.event
async def on_message(message):
    if not message.content.startswith('mega') and message.author != client.user:
        if not get(message.guild.roles,
                   name="Contributors") in message.author.roles:
            links = re.findall(r'(https?://\S+)', message.content)
            if not len(links) == 0:
                while True:
                    if 'bad' in pipeline.predict(parse_url(links)):
                        await message.delete()
                        await logging_channel.send(f"⚠️ Phishing link deleted: {message.author.mention} -> `{str(links)}` Context: ```{message.content}```")
                        break
                    break
    else:
        await client.process_commands(message)

client.run(os.getenv("TOKEN"))
