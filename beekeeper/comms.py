"""
Provides classes and methods related to communicating with the remote API
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

try:
    from urllib2 import Request as PythonRequest, urlopen, HTTPError
    from urllib import urlencode
except ImportError:
    from urllib.request import Request as PythonRequest, urlopen
    from urllib.error import HTTPError
    from urllib.parse import urlencode

import json

from beekeeper.variable_handlers import render
from beekeeper.data_handlers import decode

def download_as_json(url):
    """
    Download the data at the URL and load it as JSON
    """
    return json.loads(request(url=url).read().decode('utf-8'))

def request(*args, **kwargs):
    """
    Make a request with the received arguments and return an
    HTTPResponse object
    """
    req = PythonRequest(*args, **kwargs)
    return urlopen(req)

class Request(object):

    """
    Holds data and provides methods related to building and sending
    an HTTP request with the data passed to it
    """

    def __init__(self, action, variables, verbose=False):
        self.action = action
        self.variables = variables
        self.verbose = verbose
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

    def print_out(self):
        """
        Print out the three base level variables of the request.
        """
        print('URL: {}'.format(self.output['url']))
        print('Headers:')
        if self.output['headers']:
            for name, val in self.output['headers'].items():
                print('{}: {}'.format(name, val))
        else:
            print('None')
        print('Data:')
        if self.output['data']:
            print(self.output['data'].decode('utf-8'))

    def send(self):
        """
        Send the request defined by the data stored in the object.
        """
        if self.verbose:
            self.print_out()
            return Response(self.action, request(**self.output))
        else:
            return Response(self.action, request(**self.output)).read()

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
        url = str(rep['value']).join(url.split('{{{}}}'.format(rep['name'])))
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

    def __init__(self, action, response):
        self.action = action
        self.headers = response.headers
        self.data = response.read()
        self.code = response.getcode()

    def mimetype(self):
        """
        Get the Content-Type header from the response. Strip
        the ";charset=xxxxx" portion if necessary. If we can't
        find it, use the predefined format.
        """
        if ';' in self.headers.get('Content-Type', ''):
            return self.headers['Content-Type'].split(';')[0]
        return self.headers.get('Content-Type', self.format())

    def format(self):
        """
        Get the hard-defined format of the parent action object
        """
        return self.action.format(direction='returns')

    def encoding(self):
        """
        Look for a "charset=" variable in the Content-Type header;
        if it's not there, just return a default value of UTF-8
        """
        if 'charset=' in self.headers.get('Content-Type', ''):
            return self.headers['Content-Type'].split('charset=')[1].split(';')[0]
        return 'utf-8'

    def cookies(self):
        """
        Get a list from the Set-Cookie header; if there's nothing
        there, return an empty list.
        """
        if self.headers.get('Set-Cookie', False):
            return self.headers.get('Set-Cookie').split('; ')
        return []

    def read(self):
        """
        Parse the body of the response using the Content-Type
        header we pulled from the response, or the hive-defined
        format, if such couldn't be pulled automatically.
        """
        return decode(self.data, self.mimetype(), encoding=self.encoding())

    def read_raw(self):
        """
        Return the bytes we got from the server without any extra
        decoding or anything; could be useful for debugging.
        """
        return self.data
