from discord.ext import commands
import discord
import datetime
from utils import parse_url, get_domain, nsfw, get_logging_channel, get_trusted_urls
import re
from discord.utils import get
from discord.ext import commands, tasks
import joblib
import sklearn
from main import get_pipeline

class Phishing(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='predict')
    async def predict(self, ctx, *, args):
        result = "safe" if get_pipeline().predict([parse_url(args)
                                         ])[0] != "bad" else "not safe"
        await ctx.reply(f"Predicted `{result}`")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.user:

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

                if 'bad' in get_pipeline().pipeline.predict(
                        parse_url(filtered_links)) and len(filtered_links) > 0:
                    await message.delete()
                    await get_logging_channel(message).send(
                        f"⚠️ Phishing link(s) deleted: {message.author.mention} -> `{str(filtered_links)}` Context: ```{message.content}```"
                    )
                return

def setup(client):
    """Every cog needs a setup function like this."""
    client.add_cog(Phishing(client))