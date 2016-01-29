"""
Provides classes and methods related to communicating with the remote API
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

try:
    from urllib2 import Request as PythonRequest, HTTPError
    from urllib2 import build_opener, HTTPCookieProcessor
    from urllib import urlencode
    import httplib
    import cookielib

except ImportError:
    from urllib.request import Request as PythonRequest, build_opener
    from urllib.request import HTTPCookieProcessor
    from urllib.error import HTTPError
    from urllib.parse import urlencode
    import http.client as httplib
    import http.cookiejar as cookielib

from beekeeper.variable_handlers import render
from beekeeper.data_handlers import decode
from beekeeper.exceptions import TraversalError

try:
    basestring
except NameError:
    basestring = str

COOKIE_JAR = cookielib.CookieJar()
REQUEST_OPENER = build_opener(HTTPCookieProcessor(COOKIE_JAR))

def download_as_json(url):
    """
    Download the data at the URL and load it as JSON
    """
    try:
        return Response('application/json', request(url=url)).read()
    except HTTPError as err:
        raise ResponseException('application/json', err)

def request(*args, **kwargs):
    """
    Make a request with the received arguments and return an
    HTTPResponse object
    """
    req = PythonRequest(*args, **kwargs)
    return REQUEST_OPENER.open(req)

class Request(object):

    """
    Holds data and provides methods related to building and sending
    an HTTP request with the data passed to it
    """

    def __init__(self, action, variables, traversal=None, _verbose=False):
        self.action = action
        self.variables = variables
        self.verbose = _verbose
        self.traversal = traversal
        self.render_variables()

    def render_variables(self):
        """
        Take the variables passed in during init and parse them
        into the base level variables we can actually do stuff with.
        """
        self.params = {}
        self.output = {}
        self.output['data'] = None
        self.output['headers'] = {}
        self.output['url'] = self.action.endpoint.url()
        for var_type in self.variables.types():
            for var in render(var_type, **self.variables.vals(var_type)):
                self.set(var)
        self.output['url'] = self.output['url'] + self.param_string()

    def send(self):
        """
        Send the request defined by the data stored in the object.
        """
        with VerboseContextManager(verbose=self.verbose):
            try:
                resp = Response(self.action.format(), request(**self.output))
            except HTTPError as err:
                raise ResponseException(self.action.format(), err)
        if self.verbose:
            return resp
        else:
            return resp.read(traversal=self.traversal)

    def set(self, variable):
        """
        Set the received base-level variable in the object
        """
        method_map = {
            'url_param': self.set_url_param,
            'header': self.set_header,
            'url_replacement': self.set_url_replacement,
            'data': self.set_data
        }
        if variable['type'] in method_map:
            method_map[variable['type']](variable)
        else:
            raise Exception('Cannot handle final variables of type {}'.format(variable['type']))

    def set_header(self, header):
        """
        Set a base-level header variable to have the given value
        """
        self.output['headers'][header['name']] = header['value']

    def set_data(self, data):
        """
        Set the base-level data variable to contain the given
        data, and also set the Content-Type header to the relevant
        value.
        """
        self.output['data'] = data['data']

    def set_url_param(self, param):
        """
        Set the base-level URL parameter variable to have the given value
        """
        self.params[param['name']] = param['value']

    def set_url_replacement(self, rep):
        """
        Do a partial format of the string with just the variable in question
        """
        url = self.output['url']
        url = str(rep['value']).join(url.split('{' + rep['name'] + '}'))
        self.output['url'] = url

    def param_string(self):
        """
        urlencode all known params, add a ? to the front, and return.
        """
        if self.params:
            return '?' + urlencode(self.params)
        return ''

class Response(object):

    """
    Stores data and provides methods related to the response that
    we get back from the API provider's server
    """

    def __init__(self, static_format, response):
        self.static_format = static_format
        self.headers = response.headers
        self.data = response.read()
        self.code = response.getcode()
        self.message = response.msg

    def mimetype(self):
        """
        Get the Content-Type header from the response. Strip
        the ";charset=xxxxx" portion if necessary. If we can't
        find it, use the predefined format.
        """
        if ';' in self.headers.get('Content-Type', ''):
            return self.headers['Content-Type'].split(';')[0]
        return self.headers.get('Content-Type', self.static_format)

    def encoding(self):
        """
        Look for a "charset=" variable in the Content-Type header;
        if it's not there, just return a default value of UTF-8
        """
        if 'charset=' in self.headers.get('Content-Type', ''):
            return self.headers['Content-Type'].split('charset=')[1].split(';')[0]
        return 'utf-8'

    def read(self, raw=False, traversal=None):
        """
        Parse the body of the response using the Content-Type
        header we pulled from the response, or the hive-defined
        format, if such couldn't be pulled automatically.
        """
        if not raw:
            response_body = decode(self.data, self.mimetype(), encoding=self.encoding())
            if traversal:
                response_body = traverse(response_body, *traversal)
            return response_body
        else:
            return self.data

def traverse(obj, *path, **kwargs):
    """
    Traverse the object we receive with the given path. Path
    items can be either strings or lists of strings (or any
    nested combination thereof). Behavior in given cases is
    laid out line by line below.
    """
    if path:
        if isinstance(obj, list):
            #If the current state of the object received is a
            #list, return a list of each of its children elements,
            #traversed with the current state of the string
            return [traverse(x, *path) for x in obj]
        elif isinstance(obj, dict):
            #If the current state of the object received is a
            #dictionary, do the following...
            if isinstance(path[0], list):
                #If the current top item in the path is a list,
                #return a dictionary with keys to each of the
                #items in the list, each traversed recursively.
                for x in path[0]:
                    if not isinstance(x, basestring):
                        raise TraversalError(obj, path[0])
                return {name: traverse(obj[name], *path[1:], split=True) for name in path[0]}
            elif not isinstance(path[0], basestring):
                #If the key isn't a string (or a list; handled
                #previously), raise an exception.
                raise TraversalError(obj, path[0])
            elif path[0] == '*':
                #If the key is a wildcard, return a dict containing
                #each item, traversed down recursively.
                return {name: traverse(item, *path[1:], split=True) for name, item in obj.items()}
            elif path[0] in obj:
                #The individual key is in the current object;
                #traverse it and return the result.
                return traverse(obj[path[0]], *path[1:])
            else:
                #The individual key doesn't exist in the
                #current object; raise an error
                raise TraversalError(obj, path[0])
        else:
            #If the current object isn't either a list or
            #a dict, then do one of two things:
            if kwargs.get('split', False):
                #If the previously-recursed operation caused
                #a split in a dict, just return the object; it's
                #been specifically called out, but it isn't
                #possible to recurse further.
                return obj
            else:
                #The object can't be traversed, and we didn't
                #specifically call it out to do something
                #else with. Raise an exception.
                raise TraversalError(obj, path[0])
    else:
        #If there's no path left, then just return the
        #object that we received.
        return obj

class ResponseException(Response, Exception):
    """
    The exception we raise when we get an HTTPError back from
    the remote server. It's here and not in beekeeper.exceptions
    because it inherits from Response, and we need to avoid
    circular dependencies.
    """

    def __init__(self, static_format, response):
        Response.__init__(self, static_format, response)

    def __str__(self):
        return 'Error message: {}/{}'.format(self.code, self.message)

class VerboseContextManager(object):
    """
    Sets httplib to verbose on __enter__; returns it to its
    previous state on __exit__.
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.previous_state = httplib.HTTPConnection.debuglevel

    def __enter__(self):
        if self.verbose:
            httplib.HTTPConnection.debuglevel = 1

    def __exit__(self, *args, **kwargs):
        httplib.HTTPConnection.debuglevel = self.previous_state
