"""
This module contains all the beekeeper classes that are used on the front end
to directly interface between the developer and the remote API.
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

import copy
from functools import partial
from keyword import iskeyword

from beekeeper.variables import Variables
from beekeeper.hive import Hive
from beekeeper.comms import Request

class Endpoint(object):

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
        return self.parent.base_url() + self.path

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

class APIObject(object):

    """
    Holds Action objects in the appropriate namespace, and provides a __getitem__
    dundermethod so that we can subscript by object ID when such exists
    """

    def __init__(self, parent, actions, **kwargs):
        self.description = kwargs.get('description', None)
        self.id_variable = kwargs.get('id_variable', None)
        if iskeyword(self.id_variable):
            self.id_variable = '_' + self.id_variable
        self.actions = {}
        for name, action in actions.items():
            self.add_action(name, parent, action)

    def __getitem__(self, key):
        """
        Allows us to subscript, dictionary-style, on the object if we
        know what the object's unique key is.
        """
        if self.id_variable:
            return APIObjectInstance(self, key)
        raise TypeError('Object cannot be addressed by ID')

    def defined_actions(self):
        """
        Get a list of the available Actions on the APIObject.
        """
        return [name for name in self.actions]

    def add_action(self, name, parent, action):
        """
        Add a single Action to the APIObject.
        """
        if iskeyword(name):
            name = '_' + name
        self.actions[name] = parent.new_action(**action)
        setattr(self, name, self.actions[name].execute)

class APIObjectInstance(object):
    """
    Ephemeral class that gets created/destroyed when the developer subscripts
    an APIObject; basically, the point is to execute an action with the subscripted
    key passed to it, as below; the two statements are equivalent:

    >>> ExampleAPI.Objects[123].update(varname=value)

    >>> ExampleAPI.Objects.update(object_id=123, varname=value)

    If assigned to a variable, it can be used directly - generally useful when
    subscripting gives you access to an object that can be used to access other
    objects; an example from the MBTA API:

    >>> OrangeLine = mbta.Routes['Orange']

    >>> OrangeLine.stops()

    >>> OrangeLine.alerts()
    """

    def __init__(self, api_object, id_key):
        self.api_object = api_object
        self.id_key = id_key
        self.actions = api_object.defined_actions

    def __getattr__(self, name):
        """
        If the action is one available on the parent APIObject, generate a
        partial with the ID variable set to have the value passed during
        initialization.
        """
        if name in self.actions():
            action = getattr(self.api_object, name)
            return partial(action, **{self.api_object.id_variable: self.id_key})
        else:
            raise AttributeError

class Action(object):

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

class API(object):

    """
    Holds global-level settings and provides initialization methods
    """

    def __init__(self, hive, *args, **kwargs):
        self._root = hive.get('root')
        self._mimetype = hive.get('mimetype', 'application/json')
        self._vars = Variables(**hive.get('variables', {})).fill(*args, **kwargs)
        self._endpoints = {}
        for name, endpoint in hive['endpoints'].items():
            self.add_endpoint(name, **endpoint)
        for name, obj in hive['objects'].items():
            self.add_object(name, obj)

    @classmethod
    def from_hive_file(cls, fname, *args, **kwargs):
        """
        Open a local JSON hive file and initialize from the hive contained
        in that file, paying attention to the version keyword argument.
        """
        version = kwargs.pop('version', None)
        return cls(Hive.from_file(fname, version), *args, **kwargs)

    @classmethod
    def from_remote_hive(cls, url, *args, **kwargs):
        """
        Download a JSON hive file from a URL, and initialize from it,
        paying attention to the version keyword argument.
        """
        version = kwargs.pop('version', None)
        return cls(Hive.from_url(url, version), *args, **kwargs)

    def variables(self):
        """
        Return a copy of the API-level variables.
        """
        return copy.deepcopy(self._vars)

    def add_endpoint(self, name, **kwargs):
        """
        Add an endpoint with the given name to the API.
        """
        self._endpoints[name] = Endpoint(self, **kwargs)

    def add_object(self, name, obj):
        """
        Initialize an APIObject with the given name and make it available
        using dot notation from the top-level namespace.
        """
        if iskeyword(name):
            name = '_' + name
        setattr(self, name, APIObject(self, **obj))

    def new_action(self, endpoint, **kwargs):
        """
        Initialize a new Action linked to the named Endpoint that's
        a member of the API.
        """
        return self._endpoints[endpoint].new_action(**kwargs)

    def format(self):
        """
        Provide the API-level MIME type.
        """
        return self._mimetype

    def base_url(self):
        """
        Provides the API base URL.
        """
        return self._root
