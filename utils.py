import json
import urllib.request

def download_as_json(url):
    return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))