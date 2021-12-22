# urls
import re
import tldextract
import time

# nsfw
from nudenet import NudeClassifierLite
import urllib.request

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


def nsfw(classifier, attachments):
    print(attachments)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] #Downloads the attachement
    urllib.request.install_opener(opener)
    for attachment in attachments:
        uuid = str(time.time())
        urllib.request.urlretrieve(attachment, f"{uuid}.png")
        print("downloaded")
        file = classifier.classify(f"{uuid}.png")
        print(file)
        return file