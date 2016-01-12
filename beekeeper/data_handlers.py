"""
This module provides methods to parse various data
types into and out of binary form. Similar way of
doing things to variable_handlers; we map MIME types
to format-specific classes in a dictionary, and then
have a generic "run" method that directs requests
passed to it to the correct format-specific method.
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import json
from functools import partial

class JSONParser:

    @staticmethod
    def dump(python_object, encoding):
        if python_object:
            return bytes(json.dumps(python_object), encoding=encoding)

    @staticmethod
    def load(response, encoding):
        return json.loads(response.decode(encoding))

class HTTPFormEncoder:

    @staticmethod
    def dump(python_object, encoding):
        if python_object:
            return bytes(urlencode(python_object), encoding=encoding)

class PlainText:

    @staticmethod
    def dump(python_object, encoding):
        if python_object:
            return bytes(str(python_object), encoding=encoding)

    @staticmethod
    def load(response, encoding):
        return response.decode(encoding)

class Binary:

    @staticmethod
    def dump(python_object, encoding):
        if python_object:
            return python_object

    @staticmethod
    def load(response, encoding):
        return response

MIMETYPES = {
    'application/json': JSONParser,
    'application/x-www-form-urlencoded': HTTPFormEncoder,
    'text/plain': PlainText,
    'text/html': PlainText
}

def code(action, data, mimetype, encoding='utf-8'):
    if action == 'dump' and isinstance(data, bytes):
        return getattr(Binary, action)(data, encoding)
    if mimetype in MIMETYPES and getattr(MIMETYPES[mimetype], action, None):
        return getattr(MIMETYPES[mimetype], action)(data, encoding)
    else:
        raise Exception('Cannot parse MIME type {}'.format(mimetype))

encode = partial(code, 'dump')
decode = partial(code, 'load')
