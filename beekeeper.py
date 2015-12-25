import copy
from variables import Variables
from hive import Hive
from parsers import decode
from utils import request

class Endpoint:

    def __init__(self, parent, path, methods=['GET'], variables={}, mimetype=None):
        self.parent = parent
        self.path = path
        self.vars = Variables(**variables)
        self.methods = methods
        self.mimetype = mimetype

    def variables(self):
        return self.parent.variables().add(**self.vars)

    def url(self):
        return self.parent.root + self.path

    def new_action(self, method='GET', **kwargs):
        if method not in self.methods:
            raise TypeError("{} not in valid method(s): {}.".format(method, self.methods))
        return Action(self, method, **kwargs)

    def format(self):
        if self.mimetype:
            return self.mimetype
        else:
            return self.parent.format()

class APIObject:

    def __init__(self, parent, actions, description=None, id_variable=None):
        self.description = description
        self.actions = actions
        self.id_variable = id_variable
        for name, action in self.actions.items():
            setattr(self, name, parent.new_action(**action).execute)

    def __getitem__(self, key):
        if "get" in self.actions and self.id_variable:
            return self.get(**{self.id_variable:key})
        raise TypeError("Object cannot be addressed by ID")

class Action:

    def __init__(self, endpoint, method, variables={}, mimetype=None):
        self.endpoint = endpoint
        self.method = method
        self.vars = Variables(**variables)
        self.mimetype = mimetype
        self.url = endpoint.url

    def variables(self):
        return self.endpoint.variables().add(**self.vars)

    def execute(self, *args, **kwargs):
        variables = self.variables().fill(*args, **kwargs)
        return decode(request(**variables.render(self)),self.format(direction='returns'))
        
    def format(self, direction='both'):
        if self.mimetype and direction in self.mimetype:
            return self.mimetype[direction]
        else:
            return self.endpoint.format()

class API:

    def __init__(self, root, variables, mimetype, *args, **kwargs):
        self.settings = Variables(**variables).fill(*args, **kwargs)
        self.mimetype = mimetype
        self.root = root
        self.endpoints = {}

    @classmethod
    def from_hive(cls, hive, *args, **kwargs):
        h = hive
        this_api = cls(h['root'], h['variables'], h['mimetype'], *args, **kwargs)
        for name, ep in h['endpoints'].items():
            this_api.add_endpoint(name, **ep)
        for name, obj in h['objects'].items():
            this_api.add_object(name, obj)
        return this_api

    @classmethod
    def from_hive_file(cls, fname, *args, version=None, **kwargs):
        return cls.from_hive(Hive.from_file(fname, version), *args, **kwargs)

    @classmethod
    def from_remote_hive(cls, url, *args, version=None, **kwargs):
        return cls.from_hive(Hive.from_url(url, version), *args, **kwargs)

    def variables(self):
        return copy.deepcopy(self.settings)

    def add_endpoint(self, name, **kwargs):
        self.endpoints[name] = Endpoint(self, **kwargs)

    def add_object(self, name, obj):
        setattr(self, name, APIObject(self, **obj))

    def new_action(self, endpoint, **kwargs):
        return self.endpoints[endpoint].new_action(**kwargs)

    def format(self):
        return self.mimetype
