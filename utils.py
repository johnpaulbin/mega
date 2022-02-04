# urls
import re
import tldextract
from discord.utils import get
import discord, json
import string


def parse_url(url):
    if isinstance(url, list):
        for idx, i in enumerate(url):
            if i.startswith('http'):
                url[idx] = re.sub(r'https?://', '', i)
            if i.startswith('www.'):
                url[idx] = re.sub(r'www.', '', i)
        return url
    else:
        if url.startswith('http'):
            url = re.sub(r'https?://', '', url)
        if url.startswith('www.'):
            url = re.sub(r'www.', '', url)
        return url


def get_domain(url):
    return tldextract.extract(parse_url(url)).registered_domain


def get_logging_channel(message):
    return get(message.guild.channels, name="automod-log")


def normalize_text(text, sym_spell):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ''.join(text.split())
    return sym_spell.word_segmentation(text).corrected_string


def lastMessage(channel, users_id):
    oldestMessage = None
    fetchMessage = await channel.history(limit = 10).find(lambda m: m.author.id == users_id)
    if fetchMessage is None:
        return ""

    if oldestMessage is None:
        oldestMessage = fetchMessage
    else:
        if fetchMessage.created_at > oldestMessage.created_at:
            oldestMessage = fetchMessage

    if (oldestMessage is not None):
        return oldestMessage.content