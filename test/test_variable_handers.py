from __future__ import unicode_literals

import unittest

from beekeeper.variable_handlers import render, set_content_type, identity

import beekeeper.variable_handlers
'''
class fakeuuid:

    def __init__(self):
        self.hex = 'xxx'

class VariableHandlerTest(unittest.TestCase):

    def test_content_type(self):
        x = {'name': 'Content-Type', 'type': 'header', 'value': 'text/plain'}
        self.assertEqual(content_type_header('text/plain'), x)

    def test_data(self):
        x = render('data', v=dict(mimetype='text/plain', value='this is text'))
        result = list(x)
        expected = [
            {'name': 'Content-Type', 'type': 'header', 'value': 'text/plain'},
            {'type': 'data', 'value': b'this is text',}
        ]
        self.assertEqual(result, expected)

    def test_data_extra_variables(self):
        with self.assertRaises(Exception):
            x = render(x=1, y=2)

    def test_identity(self):
        result = list(identity('header', x=dict(value=1), y=dict(value=2), z=dict(value=3)))
        x = {'name': 'x', 'type': 'header', 'value': 1}
        y = {'name': 'y', 'type': 'header', 'value': 2}
        z = {'name': 'z', 'type': 'header', 'value': 3}
        self.assertEqual(len(result), 3)
        self.assertIn(x, result)
        self.assertIn(y, result)
        self.assertIn(z, result)

    def test_http_auth(self):
        expected = [
            {
                'name': 'Authorization',
                'type': 'header',
                'value': 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='
            }
        ]
        username = dict(value='username')
        password = dict(value='password')
        result = list(render('http_basic_auth', username=username, password=password))
        self.assertEqual(result, expected)

    def test_bearer_auth(self):
        expected = [
            {
                'name': 'Authorization',
                'type': 'header',
                'value': 'Bearer PUT_YOUR_TOKEN_HERE'
            }
        ]
        result = list(render('bearer_token', any_var_name = dict(value='PUT_YOUR_TOKEN_HERE')))
        self.assertEqual(result, expected)

    def test_multiple_bearer(self):
        with self.assertRaises(Exception):
            render('bearer_token', {'val1': 'thing', 'val2': 'otherthing'})

    def test_multiple_data(self):
        with self.assertRaises(Exception):
            render('data', {'val1': 'thing1', 'val2': 'thing2'})

    def test_http_form(self):
        x = render('http_form', x={'value':'whatever'}, y={'value':'thing'})
        x = list(x)
        self.assertEqual(x[0], {'name': 'Content-Type', 'value': 'application/x-www-form-urlencoded', 'type': 'header'})
        self.assertIn(x[1]['value'], [b'y=thing&x=whatever', b'x=whatever&y=thing'])

    def test_multipart(self):
        self.old_uuid4 = beekeeper.variable_handlers.uuid4
        beekeeper.variable_handlers.uuid4 = fakeuuid
        should = ('\n--xxx\nContent-Disposition: form-data; name="x"\n\nwhatever'
                  '\n--xxx\nContent-Disposition: form-data; name="y"; filename="thing.name"'
                  '\nContent-Type: text/plain\n\nplaintexthere\n--xxx--')
        othershould = ('\n--xxx\nContent-Disposition: form-data; name="y"; filename="thing.name"'
                       '\nContent-Type: text/plain\n\nplaintexthere'
                       '\n--xxx\nContent-Disposition: form-data; name="x"\n\nwhatever\n--xxx--')
        should = {'type': 'data', 'value': should.encode('utf-8')}
        othershould = {'type': 'data', 'value': othershould.encode('utf-8')}
        x = render('multipart', x={'value': 'whatever'},
            y={'value':'plaintexthere', 'mimetype':'text/plain', 'filename':'thing.name'})
        x = list(x)
        self.assertIn(x[0], [should, othershould])
        self.assertEqual(x[1]['value'],'multipart/form-data; boundary=xxx')
        beekeeper.variable_handlers.uuid4 = self.old_uuid4

    def test_cookies(self):
        should = 'thing1; thing2'
        othershould = 'thing2; thing1'
        data = {'a': {'value': 'thing1'}, 'b': {'value': 'thing2'}}
        result = list(render('cookie', **data))[0]
        self.assertIn(result['value'], [should, othershould])
'''
