import json
from urllib.parse import urlencode
from functools import partial

class Response:

    def __init__(self, response):
        self.headers = dict(response.headers)
        self.data = response.read().decode(self.encoding())

    def mimetype(self):
        if ';' in self.headers['Content-Type']:
            return self.headers['Content-Type'].split(';')[0]
        return self.headers['Content-Type']

    def encoding(self):
        if 'charset=' in self.headers['Content-Type']:
            return self.headers['Content-Type'].split('charset=')[1]
        return 'utf-8'

    def cookies(self):
        return self.headers['Set-Cookie'].split('; ')

    def headers(self):
        return self.headers

    def read(self):
        return decode(self.data, self.mimetype())

class JSONParser:

    @staticmethod
    def dump(python_object):
        if python_object:
            return bytes(json.dumps(python_object), encoding='utf-8')
        return None

    @staticmethod
    def load(response):
        return json.loads(response)

class HTTPFormEncoder:

    @staticmethod
    def dump(python_object):
        if python_object:
            return bytes(urlencode(python_object), encoding='utf-8')
        return None

class PlainText:

    @staticmethod
    def dump(python_object):
        if python_object:
            return bytes(str(python_object), encoding='utf-8')
        return None

    @staticmethod
    def load(response):
        return response

mimetypes = {
    'application/json': JSONParser,
    'application/x-www-form-urlencoded': HTTPFormEncoder,
    'text/plain': PlainText,
    'text/html': PlainText
}

def code(action, data, mimetype):
    if mimetype in mimetypes and action in mimetypes[mimetype].__dict__:
        return getattr(mimetypes[mimetype], action)(data)
    else:
        raise Exception('Cannot parse MIME type {}'.format(mimetype))

encode = partial(code, 'dump')
decode = partial(code, 'load')