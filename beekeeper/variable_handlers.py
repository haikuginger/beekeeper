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
from .data_handlers import encode

def identity(var_type, **values):
    for name, value in values.items():
        yield dict(type=var_type, name=name, value=value['value'])

def render_data(**data):
    if len(data) > 1:
        raise Exception('render_data can only receive a single data object')
    else:
        for _, val in data.items():
            yield render('header', **{'Content-Type': {'value': val['mimetype']}})
            yield {'type': 'data', 'value': encode(val['value'], val['mimetype'])}

def http_form(**values):
    form = {'x': {'value': values, 'mimetype': 'application/x-www-form-urlencoded'}}
    yield render('data', **form)

def basic_auth(**values):
    username = values.get('username', {}).get('value', '')
    password = values.get('password', {}).get('value', '')
    authinfo = base64.b64encode("{}:{}".format(username, password).encode('utf-8'))
    authinfo = 'Basic {}'.format(authinfo.decode('utf-8'))
    return render('header', Authorization={"value": authinfo})

def cookies(**values):
    cookie = {'value':'; '.join([value['value'] for _, value in values.items()])}
    return render('header', Cookie=cookie)

def empty(**_):
    return []

def multipart(**values):
    boundary = uuid4().hex
    files = {name: data for name, data in values.items() if data['mimetype'] != 'form-data'}
    form_fields = {name: field for name, field in values.items() if data['mimetype'] == 'form-data'}
    output = b''
    for x in form_entry(boundary, **form_fields):
        output += x
    for x in file_entry(boundary, **files):
        output += x
    output += b'--' + bytes(boundary, encoding='utf-8') + b'--'
    yield output
    yield render('header', **{'Content-Type': 'multipart/form-data; boundary={}'.format(boundary)})

    def form_entry(outer_bound, **values):

        if not values:
            return []
        for name, value in values.items():
            out = b'\n--' + bytes(outer_bound, encoding='utf-8')
            out += b'\nContent-Disposition: form-data; name="'+bytes(name, encoding='utf-8')+b'"'
            out += b'\n'
            out += b'\n' + bytes(value['value'], encoding='utf-8')
            yield out

    def file_entry(outer_bound, **values):

        def single_file(bound, value):
            out = b'\n--' + bytes(bound, encoding='utf-8')
            out += b'\nContent-Disposition: form-data; name="files"; filename="'
            out += bytes(value.get('filename', uuid4().hex), encoding='utf-8') + b'"'
            out += b'\nContent-Type: ' + bytes(value['mimetype'])
            out += encode(value['value'], value['mimetype'])
            return out

        if not values:
            return []
        if len(values) == 1:
            for name, value in values.items():
                yield single_file(outer_bound, value)
        else:
            inner_bound = uuid4().bytes
            out = b'\n--' + outer_bound
            out += b'\nContent-Disposition: form-data; name="files"'
            out += b'\nContent-Type: multipart/mixed; boundary=' + inner_bound
            out += b'\n'
            yield out
            for name, value in values.items():
                yield single_file(inner_bound, value)
            yield b'--' + bytes(inner_bound, encoding='utf-8') + b'--'

variable_types = {
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
    if var_type in variable_types:
        return variable_types[var_type](**values)
