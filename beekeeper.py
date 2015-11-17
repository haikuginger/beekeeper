import urllib
import json
from functools import partial

def fill_variables(variables, check_complete=True, **kwargs):
    for key in kwargs:
        if key in variables:
            variables[key]["value"] = kwargs[key]
        else:
            variables[key] = {"type": "url_param", "value": kwargs[key]}
    if check_complete:
        assert_values(**variables)
    return variables

def assert_values(**variables):
    print(variables)
    missing = [x for x in variables if 'value' not in variables[x]]
    if missing:
        raise TypeError('Hive is missing required setting(s): {}'.format(missing))

def is_header(variable):
    if variable['type'] == 'header':
        return True
    return False

def to_json_bytes(structure):
    return bytes(json.dumps(structure))


class Endpoint:

    def __init__(self, root, inherited_values, path, variables, methods):
        self.url = root + path
        self.variables = dict(inherited_values, **variables)
        self.methods = methods
        for method in methods:
            setattr(self, method, partial(self.execute,method=method))

    def execute(self, method, data=None, dataparser=to_json_bytes, **kwargs):
        if method not in self.methods:
            raise TypeError("{} not in valid method(s): {}.".format(method, self.methods))
        if dataparser and data:
            data = dataparser(data)
        final_vars = fill_variables(self.variables, **kwargs)
        final_url = self.build_url(**final_vars)
        final_headers = {h:v['value'] for h,v in final_vars.items() if is_header(v)}
        final_request = urllib.request.Request(url=final_url,
                                               data=data,
                                               headers=final_headers,
                                               method=method)
        return urllib.request.urlopen(final_request).read()

    def build_url(self, **kwargs):
        replaced_url = self.url.format({x:x['value'] for x in kwargs})

class APIObject:

    def __init__(self, parent, actions):
        for action, t in actions:
            setattr(self, action, parent.get_method(t['endpoint'],t['method']))

class API:

    def __init__(self, root, variables, **kwargs):
        self.settings = fill_variables(variables, **kwargs)
        self.root = root
        self.new_endpoint = partial(Endpoint,root,self.settings)
        self.endpoints = {}

    def add_endpoint(self, name, path, variables, methods=['GET']):
        self.endpoints[name] = self.new_endpoint(path, variables, methods)

    def add_object(self, name, actions):
        setattr(self, name, APIObject(self, actions))

    def get_method(self, endpoint_name, method):
        return getattr(self.endpoints[endpoint_name], method)