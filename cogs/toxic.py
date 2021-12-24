from discord.ext import commands
import discord
from utils import get_logging_channel
from discord.utils import get
from discord.ext import commands
from detoxify import Detoxify


class Toxic(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.model = Detoxify('unbiased-small', device='cpu')

    @commands.command(name='toxic')
    async def toxicpredict(self, ctx, *, args):
        prediction = list(self.model.predict(args).values())[0]
        msg = "VERY TOXIC" if prediction > .85 else "NOT TOXIC"
        await ctx.send(f"{msg} `{str(prediction)}`")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.client.user:
            # bypass link check if user has manage messages
            if message.author.guild_permissions.manage_messages:
                return
            prediction = list(self.model.predict(message.content).values())[0]
            if .85 < prediction:
                await message.delete()
                await get_logging_channel(message).send(
                    f"⚠️ Toxic message deleted from: {message.author.mention} Context: ```{message.content}``` with score `{prediction}`"
                )
            return


def setup(client):
    client.add_cog(Toxic(client))
