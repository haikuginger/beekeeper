import urllib.parse
import urllib.request
import json
import parsers
from functools import partial
import copy
from variable_types import header, url_replacement, url_param, Variables, Variable
from hive import Hive

def request(url, method, headers, data, parser):
    print(url)
    final_request = urllib.request.Request(url=url,
                                           data=parser.dump(data),
                                           headers=headers,
                                           method=method)
    return parser.load(urllib.request.urlopen(final_request))

class Endpoint:

    def __init__(self, parent, parser, path, methods, **kwargs):
        self.parent = parent
        self.variables = kwargs
        self.methods = methods
        self.parser = parser

    def url(self):
        return self.parent.root + self.path

    def execute(self, method, *args, data=None, parser=None, **kwargs):
        if method not in self.methods:
            raise TypeError("{} not in valid method(s): {}.".format(method, self.methods))
        final_vars = self.fill_vars(*args, **kwargs)
        final_url = self.build_url(final_vars)
        final_headers = final_vars.headers()
        return request(final_url, method, final_headers, data, parser or self.parser)

    def build_url(self, variables):
        replaced_url = self.url.format(**variables.replacements(final=True))
        return replaced_url + "?" + urllib.parse.urlencode(variables.params())

    def fill_vars(self, *args, **kwargs):
        final_vars = copy.deepcopy(self.variables)
        return final_vars.fill(*args, **kwargs)

    def new_action(self, method, **kwargs):
        if method not in self.methods:
            raise TypeError("{} not in valid method(s): {}.".format(method, self.methods))
        return Action(self, method, **kwargs)

class APIObject:

    def __init__(self, parent, actions):
        for action, t in actions.items():
            setattr(self, action, parent.get_method(t['endpoint'],t['method']))

class Action:

    def __init__(self, endpoint, method='GET', **kwargs):
        self.endpoint = endpoint
        self.method = method
        self.variables = kwargs

    def execute(self, *args, **kwargs):


class API:
    
    PARSERS = {
        "application/json": parsers.JSONParser,
        "application/octet-stream": parsers.RawParser
    }

    def __init__(self, root, variables, data_format, *args, **kwargs):
        self.settings = Variables(**variables).fill(*args, **kwargs)
        self.parser = API.PARSERS[data_format]
        self.root = root
        self.new_endpoint = partial(Endpoint,root,self.settings,self.parser)
        self.endpoints = {}

    @classmethod
    def from_hive(cls, hive, *args, **kwargs):
        h = hive
        this_api = cls(h['root'], h['variables'], h['format'], *args, **kwargs)
        for name, ep in h['endpoints'].items():
            this_api.add_endpoint(name, **ep)
        for name, obj in h['objects'].items():
            this_api.add_object(name, obj['actions'])
        return this_api

    @classmethod
    def from_hive_file(cls, fname, *args, version=None, **kwargs):
        return cls.from_hive(Hive.from_file(fname, version), *args, **kwargs)

    @classmethod
    def from_remote_hive(cls, url, *args, version=None, **kwargs):
        return cls.from_hive(Hive.from_url(url, version), *args, **kwargs)

    @classmethod
    def add_parser(cls, mimetype, parser):
        cls.PARSERS[mimetype] = parser

    def add_endpoint(self, name, path, variables, methods=['GET']):
        self.endpoints[name] = Endpoint(self, self.parser, path, methods, **variables)

    def add_object(self, name, actions):
        setattr(self, name, APIObject(self, actions))

    def get_method(self, endpoint_name, method):
        return getattr(self.endpoints[endpoint_name], method)