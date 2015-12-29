import json
import urllib.request
import base64

def download_as_json(url):
    """
    Download the data at the URL and load it as JSON
    """
    return json.loads(request(url=url).read().decode('utf-8'))

def httpbasicauth(username, password):
    """
    Take a username and password and turn it into the string
    for an HTTP Basic Authorization header
    """
    authinfo = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
    authinfo = 'Basic {}'.format(authinfo.decode('utf-8'))
    return authinfo

def request(*args, **kwargs):
    """
    Make a request with the received arguments and return an
    HTTPResponse object
    """
    req = urllib.request.Request(*args, **kwargs)
    return urllib.request.urlopen(req)