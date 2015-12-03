import urllib.parse
import urllib.request
import json
from parsers import JSONParser, RawParser
from functools import partial
import copy
from variable_types import header, url_replacement, url_param, Variables

def is_header(variable):
    return variable['type'] == 'header'

def is_param(variable):
    return variable['type'] == 'url_param'

def to_json_bytes(structure):
    if structure:
        return bytes(json.dumps(structure), encoding="utf-8")
    return None

def hive_from_version(hive, version):
    if not 'versioning' in hive or not version:
        return hive
    v = hive['versioning']
    if version == v['version']:
        return hive
    hive_urls = [x['location'] for x in v['previousVersions'] if x['version'] == version]
    if len(hive_urls) == 1:
        return get_remote_hive(hive_urls[0])
    else:
        raise KeyError('Could not determine appropriate hive for version {}'.format(version))

def request(url, method, headers, data, parser):
    final_request = urllib.request.Request(url=url,
                                           data=parser.dump(data),
                                           headers=headers,
                                           method=method)
    return parser.load(urllib.request.urlopen(final_request))

class Endpoint:

    def __init__(self, root, inherited_values, parser, path, variables, methods):
        self.url = root + path
        self.variables = inherited_values.add(**variables)
        self.methods = methods
        self.parser = parser
        for method in methods:
            setattr(self, method, partial(self.execute, method))

    def execute(self, method, *args, data=None, parser=None, **kwargs):
        if method not in self.methods:
            raise TypeError("{} not in valid method(s): {}.".format(method, self.methods))
        final_vars = self.fill_vars(*args, **kwargs)
        final_url = self.build_url(**final_vars)
        final_headers = {h:v['value'] for h,v in final_vars.items() if is_header(v)}
        return request(final_url, method, final_headers, data, parser or self.parser)

    def build_url(self, **kwargs):
        replaced_url = self.url.format(**{x:y['value'] for x,y in kwargs.items()})
        params = {x:y['value'] for x,y in kwargs.items() if is_param(y)}
        return replaced_url + "?" + urllib.parse.urlencode(params)

    def fill_vars(self, *args, **kwargs):
        final_vars = copy.deepcopy(self.variables)
        return final_vars.fill(*args, **kwargs)

class APIObject:

    def __init__(self, parent, actions):
        for action, t in actions.items():
            setattr(self, action, parent.get_method(t['endpoint'],t['method']))

class API:
    
    PARSERS = {
        "application/json": JSONParser,
        "application/octet-stream": RawParser
    }

    def __init__(self, root, variables, data_format, *args, **kwargs):
        self.settings = Variables(**variables).fill(*args, **kwargs)
        self.parser = API.PARSERS[data_format]
        self.root = root
        self.new_endpoint = partial(Endpoint,root,self.settings,self.parser)
        self.endpoints = {}

    @classmethod
    def from_hive(cls, hive, *args, version=None, **kwargs):
        h = hive_from_version(hive, version)
        this_api = cls(h['root'], h['variables'], h['format'], *args, **kwargs)
        for name, ep in h['endpoints'].items():
            this_api.add_endpoint(name, **ep)
        for name, obj in h['objects'].items():
            this_api.add_object(name, obj['actions'])
        return this_api

    @classmethod
    def from_hive_file(cls, fname, *args, version=None, **kwargs):
        hive = json.load(open(fname,'r'))
        return cls.from_hive(hive, *args, version=version, **kwargs)

    @classmethod
    def from_remote_hive(cls, url, *args, version = None, **kwargs):
        hive = urllib.request.urlopen(url).read().decode('utf-8')
        return cls.from_hive(json.loads(hive), *args, version=version, **kwargs)

    @classmethod
    def add_parser(cls, mimetype, parser):
        cls.PARSERS[mimetype] = parser

    def add_endpoint(self, name, path, variables, methods=['GET']):
        self.endpoints[name] = self.new_endpoint(path, variables, methods)

    def add_object(self, name, actions):
        setattr(self, name, APIObject(self, actions))

    def get_method(self, endpoint_name, method):
        return getattr(self.endpoints[endpoint_name], method)