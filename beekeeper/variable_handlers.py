"""
This module provides methods that parse variables into
one of the three base level variable types. We map the
variable type names to methods that can handle them. Each
method should either return an iterable (either natively
or by returning an executed generator), or should yield
single objects (in other words, be a generator).
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

from uuid import uuid4
from functools import partial
import base64

from beekeeper.data_handlers import encode

def content_type_header(mimetype):
    return {'name': 'Content-Type', 'type': 'header', 'value': mimetype}

def identity(var_type, **values):
    for name, value in values.items():
        yield dict(type=var_type, name=name, value=value['value'])

def render_data(**data):
    if len(data) > 1:
        raise Exception('render_data can only receive a single data object')
    else:
        for _, val in data.items():
            yield content_type_header(val['mimetype'])
            yield {'type': 'data', 'data': encode(val['value'], val['mimetype'])}

def http_form(**values):
    form = {'x': {'value': values, 'mimetype': 'application/x-www-form-urlencoded'}}
    for each in render('data', **form):
        yield each

def basic_auth(**values):
    username = values.get('username', {}).get('value', '')
    password = values.get('password', {}).get('value', '')
    authinfo = base64.b64encode("{}:{}".format(username, password).encode('utf-8'))
    authinfo = 'Basic {}'.format(authinfo.decode('utf-8'))
    for each in render('header', Authorization={"value": authinfo}):
        yield each

def cookies(**values):
    cookie = {'value':'; '.join([value['value'] for _, value in values.items()])}
    for each in render('header', Cookie=cookie):
        yield each

def empty(**_):
    return []

def multipart(**values):
    frame = '\n--{}\nContent-Disposition: form-data; name="{}"'
    boundary = uuid4().hex
    files = [name for name, data in values.items() if data.get('mimetype', False)]
    output = bytes()
    for name, value in values.items():
        if name in files:
            this_frame = frame + '; filename="{}"\nContent-Type: {}\n\n'
            this_data = encode(value['value'], value['mimetype'])
            args = (boundary, name, value.get('filename', uuid4().hex), value['mimetype'])
        else:
            this_frame = frame + '\n\n'
            this_data = bytes(value['value'], encoding='ascii')
            args = (boundary, name)
        output += bytes(this_frame.format(*args), encoding='ascii') + this_data
    output += bytes('\n--{}--'.format(boundary), encoding='ascii')
    yield {'type': 'data', 'data': output}
    yield content_type_header('multipart/form-data; boundary={}'.format(boundary))

VARIABLE_TYPES = {
    'http_form': http_form,
    'header': partial(identity, 'header'),
    'data': render_data,
    'url_replacement': partial(identity, 'url_replacement'),
    'url_param': partial(identity, 'url_param'),
    'http_basic_auth': basic_auth,
    'cookie': cookies,
    'multipart': multipart
}

def render(var_type, **values):
    if var_type in VARIABLE_TYPES:
        return VARIABLE_TYPES[var_type](**values)
