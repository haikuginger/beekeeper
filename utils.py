import json
import urllib.request
import base64

def download_as_json(url):
    return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))

def httpbasicauth(username, password):
    authinfo = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
    authinfo = "Basic {}".format(authinfo.decode('utf-8'))
    return authinfo

def request(*args, **kwargs):
    req = urllib.request.Request(*args, **kwargs)
    return urllib.request.urlopen(req)