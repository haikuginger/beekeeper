import json
from urllib.parse import urlencode
from functools import partial

class JSONParser:

    @staticmethod
    def dump(python_object):
        if python_object:
            return bytes(json.dumps(python_object), encoding='utf-8')
        return None

    @staticmethod
    def load(response):
        return json.loads(response.read().decode('utf-8'))

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
        return response.read().decode('utf-8')

def code(action, data, mimetype):
    if mimetype in mimetypes and action in mimetypes[mimetype].__dict__:
        return getattr(mimetypes[mimetype], action)(data)
    else:
        raise Exception('Cannot parse MIME type {}'.format(mimetype))

mimetypes = {
    'application/json': JSONParser,
    'application/x-www-form-urlencoded': HTTPFormEncoder,
    'text/plain': PlainText,
    'text/html': PlainText
}

encode = partial(code, 'dump')
decode = partial(code, 'load')