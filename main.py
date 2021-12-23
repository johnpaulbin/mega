import discord
import os
import time
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check
import joblib
import sklearn
from utils import parse_url, get_domain, nsfw, get_logging_channel, get_trusted_urls
import re
from dotenv import load_dotenv
import tldextract
import json
from nudenet import NudeClassifierLite
import asyncio
from itertools import cycle
from os import listdir

load_dotenv()
client = discord.Client()
client = commands.Bot(command_prefix='mega')
nsfwclassifier = NudeClassifierLite()
pipeline = joblib.load('phishing.pkl')

if __name__ == '__main__':
    global TRUSTED_URLS
    TRUSTED_URLS = json.load(open("trust.json"))

    for cog in listdir('./cogs'):
        if cog.endswith('.py') == True:
            client.load_extension(f'cogs.{cog[:-3]}')

def get_pipeline():
    return pipeline

@client.event
async def on_ready():
    print("bot online")
    change_status.start()


@client.command()
async def trust(ctx, *, args):
    links = re.findall(r'(https?://\S+)', ctx.message.content)
    if not len(links) == 0 and get(
            ctx.message.guild.roles,
            id=836458265889079326) in ctx.message.author.roles:
        with open("trust.json", "r+") as jsfile:
            data = json.load(jsfile)
            data.update({get_domain(links[0]): "safe"})
            jsfile.seek(0)
            json.dump(data, jsfile)
            jsfile.close()
        await ctx.reply(f"Added `{get_domain(links[0])}`")
    else:
        await ctx.reply(f"No links found in message.")


@client.event
async def on_message(message):

    if len(message.attachments) > 0 and message.author != client.user:
        result = nsfw(nsfwclassifier, message.attachments)
        role = get(message.guild.roles, name='Muted')
        if result > .55:
            await message.delete()
            await message.author.add_roles(role)
            await get_logging_channel(message).send(
                f"{message.author.mention} Muted for potential NSFW content")
            await asyncio.sleep(30)
            await message.author.remove_roles(role)
            return
    
    await client.process_commands(message)


statuslist = cycle([
    'with caution',
    'with rad security measures',
])


@tasks.loop(seconds=15)
async def change_status():
    """This is a background task that loops every 16 seconds.
	The coroutine looped with this task will change status over time.
	The statuses used are in the cycle list called `statuslist`_.
	
	Documentation:
		https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html
	"""
    await client.change_presence(activity=discord.Game(next(statuslist)))


client.run(os.getenv("TOKEN"))
