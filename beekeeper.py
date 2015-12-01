import urllib.request
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
    missing = [x for x in variables if 'value' not in variables[x]]
    if missing:
        raise TypeError('Hive is missing required setting(s): {}'.format(missing))

def is_header(variable):
    if variable['type'] == 'header':
        return True
    return False

def is_param(variable):
    if variable['type'] == 'url_param':
        return True
    return False

def to_json_bytes(structure):
    return bytes(json.dumps(structure), encoding="utf-8")

def get_remote_hive(url):
    response = urllib.request.urlopen(url).read()
    return json.loads(response.decode('utf-8'))

def hive_from_version(hive, version):
    if version == hive['versioning']['version']:
        return hive
    hive_urls = [x['location'] for x in hive['versioning']['previousVersions'] if x['version'] == version]
    if len(hive_urls) == 1:
        return get_remote_hive(hive_urls[0])
    else:
        raise KeyError('Could not determine appropriate hive for version {}'.format(version))

class Endpoint:

    def __init__(self, root, inherited_values, path, variables, methods):
        self.url = root + path
        self.variables = dict(inherited_values, **variables)
        self.methods = methods
        for method in methods:
            setattr(self, method, partial(self.execute, method))

    def execute(self, method, *args, data=None, dataparser=to_json_bytes, **kwargs):
        if method not in self.methods:
            raise TypeError("{} not in valid method(s): {}.".format(method, self.methods))
        if dataparser and data:
            data = dataparser(data)
        final_vars = fill_variables(self.variables, **kwargs)
        final_url = self.build_url(**final_vars).replace(" ", "%20")
        final_headers = {h:v['value'] for h,v in final_vars.items() if is_header(v)}
        final_request = urllib.request.Request(url=final_url,
                                               data=data,
                                               headers=final_headers,
                                               method=method)
        return urllib.request.urlopen(final_request).read().decode('utf-8')

    def build_url(self, **kwargs):
        replaced_url = self.url.format(**{x:y['value'] for x,y in kwargs.items()})
        params = ['{}={}'.format(x, y['value']) for x,y in kwargs.items() if is_param(y)]
        return replaced_url + '?' + '&'.join(params)

class APIObject:

    def __init__(self, parent, actions):
        for action, t in actions.items():
            setattr(self, action, parent.get_method(t['endpoint'],t['method']))

class API:

    def __init__(self, root, variables, **kwargs):
        self.settings = fill_variables(variables, **kwargs)
        self.root = root
        self.new_endpoint = partial(Endpoint,root,self.settings)
        self.endpoints = {}

    @classmethod
    def from_hive(cls, hive, version=None, **kwargs):
        hive = hive_from_version(hive, version)
        this_api = API(hive['root'], hive['variables'], **kwargs)
        for name, ep in hive['endpoints'].items():
            this_api.add_endpoint(name, ep['path'], ep['variables'], methods=ep['methods'])
        for name, obj in hive['objects'].items():
            this_api.add_object(name, obj['actions'])
        return this_api

    @classmethod
    def from_hive_file(cls, fname, version=None, **kwargs):
        hive = json.load(open(fname,'r'))
        return API.from_hive(hive, version=version, **kwargs)

    def add_endpoint(self, name, path, variables, methods=['GET']):
        self.endpoints[name] = self.new_endpoint(path, variables, methods)

    def add_object(self, name, actions):
        setattr(self, name, APIObject(self, actions))

    def get_method(self, endpoint_name, method):
        return getattr(self.endpoints[endpoint_name], method)