"""
This module contains all the beekeeper classes that are used on the front end
to directly interface between the developer and the remote API.
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

import copy

from beekeeper.variables import Variables
from beekeeper.hive import Hive
from beekeeper.comms import Request

class Endpoint:

    """
    Contains the settings for an endpoint, as well as a backref to the API
    """

    def __init__(self, parent, path, **kwargs):
        self.parent = parent
        self.path = path
        self.vars = Variables(**kwargs.get('variables', {}))
        self.methods = kwargs.get('methods', ['GET'])
        self.mimetype = kwargs.get('mimetype', None)

    def variables(self):
        """
        Get API-level variables, and add in Endpoint-level variables.
        """
        return self.parent.variables().add(**self.vars)

    def url(self):
        """
        Combine the API-level root URL with the Endpoint's path.
        """
        return self.parent.root + self.path

    def new_action(self, method='GET', **kwargs):
        """
        Create a new Action linked to this endpoint with the given args.
        """
        if method not in self.methods:
            raise TypeError('{} not in valid method(s): {}.'.format(method, self.methods))
        return Action(self, method, **kwargs)

    def format(self):
        """
        Get the Endpoint-level mimetype, deferring to the API level settings
        if the Endpoint object doesn't have a value.
        """
        if self.mimetype:
            return self.mimetype
        else:
            return self.parent.format()

class APIObject:

    """
    Holds Action objects in the appropriate namespace, and provides a __getitem__
    dundermethod so that we can subscript by object ID when such exists
    """

    def __init__(self, parent, actions, **kwargs):
        self.description = kwargs.get('description', None)
        self.id_variable = kwargs.get('id_variable', None)
        self.keyed_get_action = kwargs.get('keyed_get_action', 'get')
        self.keyed_set_action = kwargs.get('keyed_set_action', 'update')
        self.actions = {}
        for name, action in actions.items():
            self.add_action(name, parent, action)

    def __getitem__(self, key):
        """
        Allows us to subscript, dictionary-style, on the object if we
        know what the object's unique key is.
        """
        if self.keyed_get_action in self.actions and self.id_variable:
            return getattr(self, self.keyed_get_action)(**{self.id_variable:key})
        raise TypeError('Object cannot be addressed by ID')

    def defined_actions(self):
        """
        Get a list of the available Actions on the APIObject.
        """
        return [name for name, _ in self.actions.items()]

    def add_action(self, name, parent, action):
        """
        Add a single Action to the APIObject.
        """
        self.actions[name] = parent.new_action(**action)
        setattr(self, name, self.actions[name].execute)

class Action:

    """
    Holds action-level variables and provides the .execute() method
    """

    def __init__(self, endpoint, method, **kwargs):
        self.endpoint = endpoint
        self.method = method
        self.vars = Variables(**kwargs.get('variables', {}))
        self.mimetype = kwargs.get('mimetype', None)
        self.url = endpoint.url

    def variables(self):
        """
        Grab all the variables from the Endpoint and higher, and
        add the ones that exist on the Action level.
        """
        return self.endpoint.variables().add(**self.vars)

    def execute(self, *args, **kwargs):
        """
        Fill all variables from *args and **kwargs, build the request,
        and send it. If we set the _verbose kwarg to true, then we'll
        get a Response object back instead of loaded data, and we'll also
        print the information that we're sending to the server.
        """
        _verbose = kwargs.pop('_verbose', False)
        variables = self.variables().fill(*args, **kwargs)
        return Request(self, variables, verbose=_verbose).send()

    def format(self, direction='both'):
        """
        Get the local directional MIME type; if it doesn't exist, defer
        to the Endpoint-level MIME type.
        """
        if self.mimetype and direction in self.mimetype:
            return self.mimetype[direction]
        else:
            return self.endpoint.format()

class API:

    """
    Holds global-level settings and provides initialization methods
    """

    def __init__(self, root, variables, mimetype, *args, **kwargs):
        self.settings = Variables(**variables).fill(*args, **kwargs)
        self.mimetype = mimetype
        self.root = root
        self.endpoints = {}

    @classmethod
    def from_hive(cls, hive, *args, **kwargs):
        """
        Initialize the API itself, then in order, add the hive-defined
        Endpoints, and the APIObjects and Actions that reference those
        Endpoints.
        """
        this_api = cls(hive['root'], hive['variables'], hive['mimetype'], *args, **kwargs)
        for name, endpoint in hive['endpoints'].items():
            this_api.add_endpoint(name, **endpoint)
        for name, obj in hive['objects'].items():
            this_api.add_object(name, obj)
        return this_api

    @classmethod
    def from_hive_file(cls, fname, *args, **kwargs):
        """
        Open a local JSON hive file and initialize from the hive contained
        in that file, paying attention to the version keyword argument.
        """
        version = kwargs.pop('version', None)
        return cls.from_hive(Hive.from_file(fname, version), *args, **kwargs)

    @classmethod
    def from_remote_hive(cls, url, *args, **kwargs):
        """
        Download a JSON hive file from a URL, and initialize from it,
        paying attention to the version keyword argument.
        """
        version = kwargs.pop('version', None)
        return cls.from_hive(Hive.from_url(url, version), *args, **kwargs)

    def variables(self):
        """
        Return a copy of the API-level variables.
        """
        return copy.deepcopy(self.settings)

    def add_endpoint(self, name, **kwargs):
        """
        Add an endpoint with the given name to the API.
        """
        self.endpoints[name] = Endpoint(self, **kwargs)

    def add_object(self, name, obj):
        """
        Initialize an APIObject with the given name and make it available
        using dot notation from the top-level namespace.
        """
        setattr(self, name, APIObject(self, **obj))

    def new_action(self, endpoint, **kwargs):
        """
        Initialize a new Action linked to the named Endpoint that's
        a member of the API.
        """
        return self.endpoints[endpoint].new_action(**kwargs)

    def format(self):
        """
        Provide the API-level MIME type.
        """
        return self.mimetype
