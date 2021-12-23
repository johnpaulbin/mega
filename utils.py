# urls
import re
import tldextract
from discord.utils import get

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


