from __future__ import unicode_literals

import unittest

from functools import partial

from beekeeper.variable_handlers import render
import beekeeper.variable_handlers

class VariableReceiver(object):

    def execute(self, var_type, **kwargs):
        render(self, var_type, **kwargs)

    def receive(self, expected, *args, **kwargs):
        if isinstance(expected, list):
            if kwargs:
                self.assertIn(kwargs, expected)
            else:
                self.assertIn(args[0], expected)
        elif kwargs:
            self.assertEqual(expected, kwargs)
        else:
            self.assertEqual(expected, args[0])

class fakeuuid:

    def __init__(self):
        self.hex = 'xxx'

class VariableHandlerTest(VariableReceiver, unittest.TestCase):

    def test_data(self):
        self.set_headers = partial(self.receive, {'Content-Type': 'text/plain'})
        self.set_data = partial(self.receive, b'this is text')
        self.execute('data', variable={'mimetype': 'text/plain', 'value': 'this is text'})

    def test_http_auth(self):
        self.set_headers = partial(self.receive, {'Authorization': 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='})
        username = dict(value='username')
        password = dict(value='password')
        self.execute('http_basic_auth', username=username, password=password)

    def test_bearer_auth(self):
        self.set_headers = partial(self.receive, {'Authorization': 'Bearer PUT_YOUR_TOKEN_HERE'})
        var = dict(value='PUT_YOUR_TOKEN_HERE')
        self.execute('bearer_token', var=var)

    def test_multiple_bearer(self):
        self.set_headers = partial(self.receive, {'Authorization': 'Nope'})
        with self.assertRaises(Exception):
            self.execute('bearer_token', var1='thing', var2='otherthing')

    def test_http_form(self):
        expected = [
            b'y=thing&x=whatever',
            b'x=whatever&y=thing'
        ]
        self.set_headers = partial(self.receive, {'Content-Type': 'application/x-www-form-urlencoded'})
        self.set_data = partial(self.receive, expected)
        var = dict(x={'value':'whatever'}, y={'value':'thing'})
        self.execute('http_form', **var)

    def test_multipart(self):
        self.old_uuid4 = beekeeper.variable_handlers.uuid4
        beekeeper.variable_handlers.uuid4 = fakeuuid
        should = ('\n--xxx\nContent-Disposition: form-data; name="x"\n\nwhatever'
                  '\n--xxx\nContent-Disposition: form-data; name="y"; filename="thing.name"'
                  '\nContent-Type: text/plain\n\nplaintexthere\n--xxx--')
        othershould = ('\n--xxx\nContent-Disposition: form-data; name="y"; filename="thing.name"'
                       '\nContent-Type: text/plain\n\nplaintexthere'
                       '\n--xxx\nContent-Disposition: form-data; name="x"\n\nwhatever\n--xxx--')
        options = [should, othershould]
        self.set_headers = partial(self.receive, {'Content-Type': 'multipart/form-data; boundary=xxx'})
        self.set_data = partial(self.receive, options)
        var = {'x':{'value': 'whatever'}, 'y':{'value':'plaintexthere', 'mimetype':'text/plain', 'filename':'thing.name'}}
        self.execute('multipart', **var)

    def test_cookies(self):
        expected = [{'Cookie': 'thing1; thing2'}, {'Cookie': 'thing2; thing1'}]
        var = {'a': {'value': 'thing1'}, 'b': {'value': 'thing2'}}
        self.set_headers = partial(self.receive, expected)
        self.execute('cookie', **var)
