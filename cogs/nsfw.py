import discord
from discord.ext import commands
import urllib.request
import asyncio
import mimetypes
import os
import tempfile
from discord.utils import get
from nudenet import NudeClassifierLite

# Your existing logging helper – make sure this import works
from utils import get_logging_channel


class Nsfw(commands.Cog):
    """Detects NSFW images in message attachments and mutes the author."""

    def __init__(self, client):
        self.client = client
        self.classifier = NudeClassifierLite()
        self.threshold = 0.7          # raise the threshold to avoid mass false positives
        self.mute_duration = 300      # seconds (5 minutes)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bots and messages without attachments
        if message.author.bot or not message.attachments:
            return

        # Check all attachments for NSFW content
        is_nsfw, max_score, nsfw_urls = await self.check_attachments(
            message.attachments
        )

        if not is_nsfw:
            return

        # --- Action ---
        role = get(message.guild.roles, name='Muted')
        if role is None:
            # Optionally create the role or log a warning, but don't crash
            return

        # Delete the message
        try:
            await message.delete()
        except discord.Forbidden:
            pass

        # Mute the author
        try:
            await message.author.add_roles(role)
        except discord.Forbidden:
            pass

        # Log the incident with detailed information
        log_channel = get_logging_channel(message)
        urls_str = ', '.join(nsfw_urls)
        await log_channel.send(
            f"{message.author.mention} muted for NSFW content | "
            f"score: {max_score:.3f} | attachments: {urls_str}"
        )

        # Delayed unmute
        await asyncio.sleep(self.mute_duration)
        try:
            await message.author.remove_roles(role)
        except discord.Forbidden:
            pass

    async def check_attachments(self, attachments):
        """
        Process all attachments and return:
            - is_nsfw (bool)
            - max_score (float)
            - nsfw_urls (list of attachment URLs that exceeded the threshold)
        """
        max_score = 0.0
        nsfw_urls = []

        for attachment in attachments:
            # Ignore non-image files
            mime = mimetypes.MimeTypes().guess_type(attachment.filename)[0]
            if not mime or not mime.startswith('image/'):
                continue

            try:
                score = await self._classify_attachment(attachment.url)
            except Exception as e:
                # Log the error but continue with other attachments
                print(f"Error classifying {attachment.url}: {e}")
                continue

            if score > self.threshold:
                max_score = max(max_score, score)
                nsfw_urls.append(attachment.url)

        return max_score > self.threshold, max_score, nsfw_urls

    async def _classify_attachment(self, url):
        """
        Download an image URL, run NudeNet in a thread, and return the 'unsafe' score.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._sync_download_and_classify, url
        )

    def _sync_download_and_classify(self, url):
        """
        Synchronous part: download image → save to temp file → classify → delete temp file.
        """
        # Create a unique temporary file; NudeNet expects a real image file
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp.close()          # we'll write manually
        filepath = tmp.name

        try:
            # Download with a custom User-Agent, no global opener pollution
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read()

            with open(filepath, 'wb') as f:
                f.write(data)

            # Classify using NudeNet (assumes result format: {filename: {'unsafe': float}})
            result = self.classifier.classify(filepath)
            if result and filepath in result:
                return float(result[filepath].get('unsafe', 0.0))
            return 0.0

        finally:
            # Always clean up the temp file
            try:
                os.remove(filepath)
            except OSError:
                pass


def setup(client):
    client.add_cog(Nsfw(client))
