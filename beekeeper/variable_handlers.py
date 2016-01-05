from .data_handlers import encode
from functools import partial
import base64

def identity(var_type, **values):
    for name, value in values.items():
        yield dict(type=var_type, name=name, value=value)

def render_data(**data):
    if len(data) > 1:
        raise Exception('render_data can only receive a single data object')
    else:
        for name, val in data.items():
            yield encode(val['value', val['mimetype']])

def http_form(**values):
    form = {'x': {'value': values, 'mimetype': 'application/x-www-form-urlencoded'}}
    yield render('data', **form)

def basic_auth(**values):
    username = values.get('username', '')
    password = values.get('password', '')
    authinfo = base64.b64encode("{}:{}".format(username, password).encode('utf-8'))
    authinfo = 'Basic {}'.format(authinfo.decode('utf-8'))
    return header(Authorization=authinfo)

def empty(**values):
    return []

header = partial(identity, 'header')
url_param = partial(identity, 'url_param')

variable_types = {
    'http_form': http_form,
    'header': header,
    'data': render_data,
    'url_replacement': empty,
    'url_param': url_param,
    'http_basic_auth': basic_auth
}

def render(var_type, **values):
    if var_type in variable_types:
        return variable_types[var_type](**values)