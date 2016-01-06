"""
This module provides methods to parse various data
types into and out of binary form. Similar way of
doing things to variable_handlers; we map MIME types
to format-specific classes in a dictionary, and then
have a generic "run" method that directs requests
passed to it to the correct format-specific method.
"""

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