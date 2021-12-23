from discord.ext import commands
import discord
from utils import get_logging_channel
from discord.utils import get
from discord.ext import commands
import urllib
from nudenet import NudeClassifierLite
import os
import asyncio
import random
import mimetypes


def nsfw_check(classifier, attachments):
    for attachment in attachments:
        filetype = mimetypes.MimeTypes().guess_type(attachment.url)[0]
        filename = str(random.randint(1,9999999)) + "." + filetype.split("/")[1]
        # checking if the file is an image before downloading
        if filetype.split("/")[0] != "image":
            pass
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(attachment.url, filename)
        file = classifier.classify(filename)
        os.remove(filename)
        return file[filename]['unsafe']


class Nsfw(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.nsfwclassifier = NudeClassifierLite()

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.attachments) > 0 and message.author != self.client.user:
            result = nsfw_check(self.nsfwclassifier, message.attachments)
            role = get(message.guild.roles, name='Muted')
            if result > .55:
                await message.delete()
                await message.author.add_roles(role)
                await get_logging_channel(message).send(
                    f"{message.author.mention} Muted for potential NSFW content"
                )
                await asyncio.sleep(30)
                await message.author.remove_roles(role)
        return


def setup(client):
    client.add_cog(Nsfw(client))
