from __future__ import unicode_literals

import unittest

from beekeeper.variables import Variable, Variables, merge

variable_1 = Variable('type',**{
    'value': 'value1',
    'mimetype': 'mimetype1',
    'types': [
        'type1_1',
        'type1_2'
    ],
    'optional': True
})
variable_2 = Variable('type', **{
    'value': 'value2',
    'mimetype': 'mimetype2',
    'types': [
        'type2_1'
    ],
    'optional': False
})
variable_3 = {}
variable_4 = {
    'value': 'whatever'
}

class VariableTest(unittest.TestCase):

    def test_merge(self):
        result1 = Variable('type',**{
            'value': 'value1',
            'mimetype': 'mimetype1',
            'types': [
                'type1_1',
                'type1_2',
                'type2_1'
            ],
            'optional': True,
            'filename': None
        })
        result2 = Variable('type',**{
            'value': 'value2',
            'mimetype': 'mimetype2',
            'types': [
                'type2_1',
                'type1_1',
                'type1_2'
            ],
            'optional': False,
            'filename': None
        })
        self.assertEqual(merge(variable_1, variable_2), result2)
        self.assertEqual(merge(variable_2, variable_1), result1)
    
    def test_create_with_single_type(self):
        x = Variable('type',
                **{
                    'value': 'value2',
                    'mimetype': 'mimetype2',
                    'type':'type2_1',
                    'optional': False
                }
            )
        self.assertEqual(x, variable_2)

    def test_is_filled(self):
        filled = Variable('type',value='value')
        empty = Variable('type',value=None)
        optional = Variable('type',optional=True)
        self.assertTrue(filled.is_filled())
        self.assertFalse(empty.is_filled())
        self.assertTrue(optional.is_filled())

    def test_has_type(self):
        default_type = Variable('type')
        param = Variable('type',type='url_param')
        self.assertTrue(default_type.has_type('type'))
        self.assertTrue(param.has_type('url_param'))

    def test_has_value(self):
        no = Variable('type')
        yes = Variable('type', value='whatever')
        self.assertFalse(no.has_value())
        self.assertTrue(yes.has_value())

    def test_has_value_of_type(self):
        AA = Variable('type',value='whatever', type='url_param')
        AB = Variable('type',value='whatever', type='another')
        BA = Variable('type',type='url_param')
        BB = Variable('type',type='another')
        self.assertTrue(AA.has_value_of_type('url_param'))
        self.assertFalse(AB.has_value_of_type('url_param'))
        self.assertFalse(BA.has_value_of_type('url_param'))
        self.assertFalse(BB.has_value_of_type('url_param'))

    def test_types(self):
        var1 = Variable('type',**variable_1)
        var2 = Variable('type',**variable_2)
        var3 = Variable('type')
        self.assertEqual(list(var1.types()), variable_1['types'])
        self.assertEqual(list(var2.types()), variable_2['types'])
        self.assertEqual(list(var3.types()), ['type'])

class VariablesTest(unittest.TestCase):

    def setUp(self):
        self.variables = Variables(variable_settings=dict(default_type='type'),x=variable_1, y=variable_2)

    def test_create(self):
        self.assertEqual(self.variables, {'x':variable_1, 'y': variable_2})

    def test_types(self):
        self.variables.add(z=variable_3, a=variable_4)
        self.assertIn('type1_1', self.variables.types())
        self.assertIn('type1_2', self.variables.types())
        self.assertIn('type2_1', self.variables.types())
        self.assertIn('type', self.variables.types())

    def test_vals(self):
        self.variables.add(z=variable_4)
        self.assertEqual(self.variables.vals('type'), {'z': Variable('type',**variable_4)})

    def test_fill_kwargs(self):
        self.variables.fill_kwargs(x='value_of_x', y='value_of_y')
        self.assertEqual(self.variables['x']['value'], 'value_of_x')
        self.assertEqual(self.variables['y']['value'], 'value_of_y')

    def test_fill_args(self):
        self.variables.add(a=variable_3)
        teststr = 'this should go under a'
        self.variables.fill_arg(teststr)
        self.assertEqual(self.variables['a']['value'], teststr)

    def test_fill(self):
        self.variables.add(a=variable_3)
        teststr = 'this should go under a'
        self.variables.fill(teststr, x='valx', y='valy')
        self.assertEqual(self.variables['x']['value'], 'valx')
        self.assertEqual(self.variables['y']['value'], 'valy')
        self.assertEqual(self.variables['a']['value'], teststr)

    def test_filled_when_not(self):
        self.variables.add(a=variable_3)
        with self.assertRaises(TypeError):
            self.variables.fill()

    def test_missing_vars(self):
        self.variables.add(a=variable_3)
        self.assertEqual(self.variables.missing_vars(), ['a'])

    def test_keyword_named_variable(self):
        self.variables.add(**{'from':variable_3})
        self.assertIn('_from', self.variables)
        self.assertEqual(self.variables['_from']['name'], 'from')
