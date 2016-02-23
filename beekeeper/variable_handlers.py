"""
This module provides methods that parse variables into
one of the three base level variable types. We map the
variable type names to methods that can handle them. Each
method consumes a Request object 'rq' as the first positional
argument, and does its work by calling one of the variable-setting
methods on rq.
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

from uuid import uuid4
from functools import partial
from base64 import b64encode

from beekeeper.data_handlers import encode

def identity(**values):
    return {name: val['value'] for name, val in values.items()}

def set_content_type(rq, mimetype):
    rq.set_headers(**{'Content-Type': mimetype})

def render_data(rq, **data):
    for _, val in data.items():
        rq.set_headers(**content_type_header(val['mimetype']))
        rq.set_data(encode(val['value'], val['mimetype']))

def http_form(rq, **values):
    form = {
        'x': {
            'mimetype': 'application/x-www-form-urlencoded',
            'value': {
                name: val['value'] for name, val in values.items()
            }
        }
    }
    render(rq, 'data', **form)

def basic_auth(rq, **values):
    username = values.get('username', {}).get('value', '')
    password = values.get('password', {}).get('value', '')
    authinfo = b64encode("{}:{}".format(username, password).encode('utf-8'))
    authinfo = 'Basic {}'.format(authinfo.decode('utf-8'))
    rq.set_headers(Authorization=authinfo)

def bearer(rq, **values):
    if len(values) > 1:
        raise Exception('Only one bearer token allowed')
    else:
        for _, token in values.items():
            text = 'Bearer {}'.format(token['value'])
            rq.set_headers(Authorization=text)

def cookies(rq, **values):
    cookie = '; '.join([value['value'] for _, value in values.items()])
    rq.set_headers(Cookie=cookie)

def multipart(rq, **values):
    frame = '\n--{}\nContent-Disposition: form-data; name="{}"'
    boundary = uuid4().hex
    files = [name for name, data in values.items() if data.get('mimetype', False)]
    output = bytes()
    for name, value in values.items():
        if name in files:
            fname = value.get('filename', getattr(value['value'], 'name', uuid4().hex))
            this_frame = frame + '; filename="{}"\nContent-Type: {}\n\n'
            this_data = encode(value['value'], value['mimetype'])
            args = (boundary, name, fname, value['mimetype'])
        else:
            this_frame = frame + '\n\n'
            this_data = value['value'].encode('ascii')
            args = (boundary, name)
        output += this_frame.format(*args).encode('ascii') + this_data
    output += '\n--{}--'.format(boundary).encode('ascii')
    rq.set_data(output)
    header = 'multipart/form-data; boundary={}'.format(boundary)
    set_content_type(rq, header)

def header(rq, **values):
    rq.set_headers(**identity(**values))

def replacement(rq, **values):
    rq.set_url_replacements(**identity(**values))

def url_param(rq, **values):
    rq.set_url_params(**identity(**values))

VARIABLE_TYPES = {
    'http_form': http_form,
    'header': header,
    'data': render_data,
    'url_replacement': replacement,
    'url_param': url_param,
    'http_basic_auth': basic_auth,
    'cookie': cookies,
    'multipart': multipart,
    'bearer_token': bearer
}

def add_variable_handler(var_type, handler):
    VARIABLE_TYPES[var_type] = handler

def render(rq, var_type, **values):
    if var_type in VARIABLE_TYPES:
        variables = {val.pop('name', name): val for name, val in values.items()}
        VARIABLE_TYPES[var_type](rq, **variables)
