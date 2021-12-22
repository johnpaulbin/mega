import discord
import os
import time
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check
import joblib
import sklearn
from utils import parse_url, get_domain, nsfw
import re
from dotenv import load_dotenv
import tldextract
import json
from nudenet import NudeClassifierLite

load_dotenv()
client = discord.Client()
pipeline = joblib.load('phishing.pkl')
client = commands.Bot(command_prefix='mega')
nsfwclassifier = NudeClassifierLite()


@client.event
async def on_ready():
    global LOGGING_CHANNEL
    LOGGING_CHANNEL = client.get_channel(849427163153563708)
    global TRUSTED_URLS
    TRUSTED_URLS = json.load(open("trust.json"))
    print("bot online")


@client.command()
async def predict(ctx, *, args):
    result = "safe" if pipeline.predict([parse_url(args)
                                         ])[0] != "bad" else "not safe"
    await ctx.reply(f"Predicted `{result}`")


@client.command()
async def nude(ctx, *, args):
    if len(ctx.message.attachments) > 0:
        result = nsfw(nsfwclassifier, ctx.message.attachments)
        await ctx.reply(f"Predicted `{result}`")


@client.command()
async def trust(ctx, *, args):
    links = re.findall(r'(https?://\S+)', ctx.message.content)
    if not len(links) == 0 and get(
            ctx.message.guild.roles,
            name="Contributors") in ctx.message.author.roles:
        with open("trust.json", "r+") as jsfile:
            data = json.load(jsfile)
            data.update({get_domain(links[0]): "safe"})
            jsfile.seek(0)
            json.dump(data, jsfile)
            jsfile.close()
        global TRUSTED_URLS
        TRUSTED_URLS = json.load(open("trust.json"))
        await ctx.reply(f"Added `{get_domain(links[0])}`")
    else:
        await ctx.reply(f"No links found in message.")


@client.event
async def on_message(message):
    if not message.content.startswith(
            'mega') and message.author != client.user:
        if not get(message.guild.roles,
                   name="Contributors") in message.author.roles:
            links = re.findall(r'(https?://\S+)', message.content)
            if not len(links) == 0:
                for link in links:
                    if get_domain(link) in TRUSTED_URLS:
                        return

                if 'bad' in pipeline.predict(parse_url(links)):
                    await message.delete()
                    await LOGGING_CHANNEL.send(
                        f"⚠️ Phishing link deleted: {message.author.mention} -> `{str(links)}` Context: ```{message.content}```"
                    )
                return

    else:
        await client.process_commands(message)


client.run(os.getenv("TOKEN"))
