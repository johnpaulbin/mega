from discord.ext import commands
import discord
from utils import parse_url, get_domain, get_logging_channel
from discord.utils import get
from discord.ext import commands
from detoxify import Detoxify

class Toxic(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.model = Detoxify('unbiased-small', device='cpu')


    @commands.command(name='toxic')
    async def toxicpredict(self, ctx, *, args):
        prediction = sum(list(self.model.predict(args).values()))
        await ctx.send(str(prediction))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.client.user:

            #await message.channel.send(str(self.model.predict(message.content)))
            print()
            """
            if get(message.guild.roles,
                   id=836458265889079326) in message.author.roles:
                return
            # bypass link check if user has manage messages
            if message.author.guild_permissions.manage_messages:
                return
            
            
            if 'bad' in self.pipeline.predict(
                        parse_url(filtered_links)) and len(filtered_links) > 0:
                    await message.delete()
                    await get_logging_channel(message).send(
                        f"⚠️ Phishing link(s) deleted: {message.author.mention} -> `{str(filtered_links)}` Context: ```{message.content}```"
                    )
            """
            return

def setup(client):
    client.add_cog(Toxic(client))