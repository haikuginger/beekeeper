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

from functools import partial
import base64
from .data_handlers import encode

def identity(var_type, **values):
    for name, value in values.items():
        yield dict(type=var_type, name=name, value=value)

def render_data(**data):
    if len(data) > 1:
        raise Exception('render_data can only receive a single data object')
    else:
        for _, val in data.items():
            yield encode(val['value', val['mimetype']])

def http_form(**values):
    form = {'x': {'value': values, 'mimetype': 'application/x-www-form-urlencoded'}}
    yield render('data', **form)

def basic_auth(**values):
    authelements = values.get('username', ''), values.get('password', '')
    authinfo = base64.b64encode("{}:{}".format(*authelements).encode('utf-8'))
    authinfo = 'Basic {}'.format(authinfo.decode('utf-8'))
    return header(Authorization=authinfo)

def cookies(**values):
    return header(Cookie='; '.join([value for _, value in values.items()]))

def empty(**_):
    return []

header = partial(identity, 'header')
url_param = partial(identity, 'url_param')

variable_types = {
    'http_form': http_form,
    'header': header,
    'data': render_data,
    'url_replacement': identity,
    'url_param': url_param,
    'http_basic_auth': basic_auth
    'cookie': cookies
}

def render(var_type, **values):
    if var_type in variable_types:
        return variable_types[var_type](**values)
