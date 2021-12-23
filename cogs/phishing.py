from discord.ext import commands
import discord
from utils import parse_url, get_domain, get_logging_channel
import re
from discord.utils import get
from discord.ext import commands
import joblib
import sklearn
import json


def get_trusted_urls():
        return json.load(open("trust.json"))

class Phishing(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.pipeline = joblib.load('phishing.pkl')

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

            if message.author.guild_permissions.manage_messages:
                return

            links = re.findall(r'(https?://\S+)', message.content)
            if not len(links) == 0:

                filtered_links = []

                for link in links:
                    if get_domain(link) not in get_trusted_urls():
                        filtered_links.append(link)

                if 'bad' in self.pipeline.predict(
                        parse_url(filtered_links)) and len(filtered_links) > 0:
                    await message.delete()
                    await get_logging_channel(message).send(
                        f"⚠️ Phishing link(s) deleted: {message.author.mention} -> `{str(filtered_links)}` Context: ```{message.content}```"
                    )
                return


def setup(client):
    client.add_cog(Phishing(client))
