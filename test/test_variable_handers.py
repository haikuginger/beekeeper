from __future__ import unicode_literals

import unittest

from beekeeper.variable_handlers import render, content_type_header, identity

class VariableHandlerTest(unittest.TestCase):

    def test_content_type(self):
        x = {'name': 'Content-Type', 'type': 'header', 'value': 'text/plain'}
        self.assertEqual(content_type_header('text/plain'), x)

    def test_data(self):
        x = render('data', v=dict(mimetype='text/plain', value='this is text'))
        result = list(x)
        expected = [
            {'name': 'Content-Type', 'type': 'header', 'value': 'text/plain'},
            {'type': 'data', 'data': b'this is text',}
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

    #Can't reliably test multipart/form-data yet, since it uses random
    #separators; cookies aren't implemented yet.