import urllib
import json
from functools import partial

def fill_variables(variables, **kwargs):
    for key in kwargs:
        if key in variables:
            variables[key]["value"] = kwargs[key]
    return variables

class Endpoint:

    def __init__(self, root, inherited_values, path, variables, methods):
        self.url = root + path
        self.variables = dict(inherited_values, **variables)
        self.methods = methods
        for method in methods:
            setattr(self, method, partial(self.execute,method=method))

    def execute(self, method, *args, **kwargs):
        if method not in self.methods:
            raise ValueError("{} not in {}.".format(method, self.methods))
        #stuff to execute the query here

class APIObject:

    def __init__(self, parent, actions):
        for action, t in actions:
            setattr(self, action, parent.get_method(t['name'],t['method']))

class API:

    def __init__(self, root, variables, **kwargs):
        self.root = root
        self.settings = fill_variables(variables, **kwargs)
        self.new_endpoint = partial(Endpointelf.root,self.settings)
        self.endpoints = {}

    def add_endpoint(self, name, path, variables, methods=["GET"]):
        self.endpoints[name] = self.new_endpoint(path, variables, methods)

    def add_object(self, name, actions):
        setattr(self, name, APIObject(self, actions))

    def get_method(self, endpoint_name, method):
        return getattr(self.endpoints[endpoint_name], method)