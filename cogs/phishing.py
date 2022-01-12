from discord.ext import commands
import discord
from utils import parse_url, get_domain, get_logging_channel
import re
from discord.utils import get
from discord.ext import commands
import joblib
import sklearn
import json
from phish_detector import PhishDetector
import requests
from urllib.parse import urlparse

BANNED_KEYWORDS = [
    '<meta property="og:site_name" content="Disсоrd">', 'content="@discord"'
]


def get_trusted_urls():
    return json.load(open("trust.json"))


class Phishing(commands.Cog):
    def __init__(self, client):
        self.client = client
        #self.pipeline = joblib.load('phishing.pkl')
        self.detector = PhishDetector()

    @commands.command(name='trust')
    async def trust(self, ctx, *, args):
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
        return

    @commands.command(name='predict')
    async def predict(self, ctx, *, args):
        result = "safe" if self.pipeline.predict(
            [parse_url(args)])[0] != "bad" else "not safe"
        await ctx.reply(f"Predicted `{result}`")
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.client.user:
            if get(message.guild.roles,
                   id=836458265889079326) in message.author.roles:
                return
            # bypass link check if user has manage messages
            #if message.author.guild_permissions.manage_messages:
            #    return
            links = re.findall(r'(https?://\S+)', message.content)
            if not len(links) == 0:
                #filtered_links = []
                for link in links:

                    # this will scan currently known phishing sites via discord's database
                    if self.detector.check(link) == True:
                        await message.delete()
                        await get_logging_channel(message).send(
                            f"⚠️ Phishing link deleted: {message.author.mention} -> `{link}` Context: ```{message.content}```"
                        )
                        return

                #    if get_domain(link) not in get_trusted_urls():
                #        filtered_links.append(link)
                    print(link)
                    response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}).text
                    print(response)
                    if any(keyword in response for keyword in BANNED_KEYWORDS):
                        print("BAD!!!")
                        print(urlparse(link).netloc.split('.')[1:])
                        if not any(urlparse(link).netloc.split('.')[1:] in url for url in ["discord.com", "discordapp.com", "discord.net", "discordapp.net"]):
                            
                            await message.delete()
                            await get_logging_channel(message).send(
                            f"⚠️ Phishing link deleted: {message.author.mention} -> `{link}` Context: ```{message.content}```"
                            )
                            return


                """
                if 'bad' in self.pipeline.predict(
                        parse_url(filtered_links)) and len(filtered_links) > 0:
                    await message.delete()
                    await get_logging_channel(message).send(
                        f"⚠️ Phishing link(s) deleted: {message.author.mention} -> `{str(filtered_links)}` Context: ```{message.content}```"
                    )
                return
                """


def setup(client):
    client.add_cog(Phishing(client))
