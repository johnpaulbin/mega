# urls
import re
import tldextract
import time

# nsfw
from nudenet import NudeClassifierLite
import urllib.request
import os

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
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    for attachment in attachments:
        req = urllib.request.Request(attachment.url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req)
        filename = r.info().get_filename()

        urllib.request.urlretrieve(attachment.url, f"{filename}")

        if 'video' in r.getheader('Content-Type'):
            file = classifier.classify_video(filename)
            print(file)
            return 0.01
          
        else:
            file = classifier.classify(filename)
        os.remove(filename)
        return file[filename]['unsafe']