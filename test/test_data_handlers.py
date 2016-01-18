from __future__ import unicode_literals

import unittest

from beekeeper.data_handlers import encode, decode

class TestJsonParser(unittest.TestCase):

    def setUp(self):
        self.testingbytes = b'{"Key1":"Value1","Key2":2}'
        self.testingdict = {'Key1': 'Value1', 'Key2': 2}

    def test_decode(self):
        self.assertEqual(decode(self.testingbytes, 'application/json'), self.testingdict)

class TestBinary(unittest.TestCase):
    def setUp(self):
        self.to_test = b'1234567890'

    def test_encode(self):
        self.assertEqual(encode(self.to_test, 'fake-mime'), self.to_test)

    def test_decode(self):
        self.assertEqual(decode(self.to_test, 'fake-mime'), self.to_test)

class TestText(unittest.TestCase):
    def setUp(self):
        self.string = 'This is a string'
        self.bytes = b'This is a string'

    def test_encode(self):
        self.assertEqual(encode(self.string, 'text/plain'), self.bytes)

    def test_decode(self):
        self.assertEqual(decode(self.bytes, 'text/plain'), self.string)

class TestParams(unittest.TestCase):
    def setUp(self):
        self.test_params = [
            ('var1', 'val1'),
            ('var2', 'val2'),
            ('var3', 'val3'),
            ('var4', 'val4')
        ]
        self.proper_output = b'var1=val1&var2=val2&var3=val3&var4=val4'

    def test_encode(self):
        self.assertEqual(encode(self.test_params, 'application/x-www-form-urlencoded'), self.proper_output)
