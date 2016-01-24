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
from base64 import b64encode

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
    form = {
        'x': {
            'mimetype': 'application/x-www-form-urlencoded',
            'value': {
                name: val['value'] for name, val in values.items()
            }
        }
    }
    return render('data', **form)

def basic_auth(**values):
    username = values.get('username', {}).get('value', '')
    password = values.get('password', {}).get('value', '')
    authinfo = b64encode("{}:{}".format(username, password).encode('utf-8'))
    authinfo = 'Basic {}'.format(authinfo.decode('utf-8'))
    return render('header', Authorization={"value": authinfo})

def bearer(**values):
    if len(values) > 1:
        raise Exception('Only one bearer token allowed')
    else:
        for _, token in values.items():
            text = 'Bearer {}'.format(token['value'])
            return render('header', Authorization={'value': text})

def cookies(**values):
    cookie = {'value':'; '.join([value['value'] for _, value in values.items()])}
    return render('header', Cookie=cookie)

def multipart(**values):
    frame = '\n--{}\nContent-Disposition: form-data; name="{}"'
    boundary = uuid4().hex
    files = [name for name, data in values.items() if data.get('mimetype', False)]
    output = bytes()
    for name, value in values.items():
        if name in files:
            fname = value.get('filename', uuid4().hex)
            this_frame = frame + '; filename="{}"\nContent-Type: {}\n\n'
            this_data = encode(value['value'], value['mimetype'])
            args = (boundary, name, fname, value['mimetype'])
        else:
            this_frame = frame + '\n\n'
            this_data = value['value'].encode('ascii')
            args = (boundary, name)
        output += this_frame.format(*args).encode('ascii') + this_data
    output += '\n--{}--'.format(boundary).encode('ascii')
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
    'multipart': multipart,
    'bearer_token': bearer
}

def render(var_type, **values):
    if var_type in VARIABLE_TYPES:
        variables = {val.pop('name', name): val for name, val in values.items()}
        return VARIABLE_TYPES[var_type](**variables)
