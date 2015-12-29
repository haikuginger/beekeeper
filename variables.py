from functools import partial
from urllib.parse import urlencode
from parsers import encode

def is_var(var):
    return isinstance(var, Variable)

def merge(var1, var2):
    """
    Take two copies of a variable and reconcile them. var1 is assumed
    to be the higher-level variable, and so will be overridden by var2
    where such becomes necessary.
    """
    out = {}
    out['value'] = var2.get('value', var1.get('value', None))
    out['types'] = list(set(var1['types'],var2['types']))
    out['optional'] = var2.get('optional', False)
    

class Variable(dict):

    def __init__(self, **kwargs):
        kwargs['types'] = kwargs.get('types', [])
        if not kwargs['types']:
            kwargs['types'].append(kwargs.get('type', 'url_param'))
        super().__init__(**kwargs)

    def is_filled(self):
        if self.has_value() or self.get('optional', False):
            return True
        return False

    def has_type(self, var_type):
        if var_type in self['types']:
            return True
        return False

    def has_value(self):
        if self.get('value', None) is not None:
            return True
        return False

class Variables(dict):

    def __init__(self, **kwargs):
        super().__init__()
        self.add(**kwargs)
        self.headers = partial(self.vals, 'header')
        self.replacements = partial(self.vals, 'url_replacement')
        self.params = partial(self.vals, 'url_param')
        self.form = partial(self.vals, 'http_form')

    def render(self, action):
        return_dict = {}
        url = action.url().format(**self.replacements(final=True))
        url += '?' + urlencode(self.params(final=True))
        return_dict['url'] = url
        return_dict['headers'] = self.headers(final=True)
        mimetype = action.format('takes')
        data = self.data()
        if self.form() and not data:
            mimetype = 'application/x-www-form-urlencoded'
            data = self.form(final=True)
        return_dict['headers']['Content-Type'] = mimetype
        return_dict['data'] = encode(data, mimetype)
        return return_dict

    def data(self):
        data = [y for x,y in self.vals('data').items()]
        if data:
            if len(data) == 1:
                return data[0]
            else:
                raise TypeError('Only one data-type variable can have a value')
        return None

    def vals(self, var_type, final=False):
        if final:
            self.assert_full()
        return {x:y['value'] for x,y in self.items() if y.has_type(var_type) and y.has_value()}

    def add(self, **kwargs):
        for name, var in kwargs.items():
            if name in self:
                self[name] = merge(self[name], var)
            else:
                self[name] = Variable(**var)
        return self

    def fill_arg(self, *args):
        missing = self.missing_vars()
        if 1 == len(args) == len(missing):
            self.setval(missing[0], args[0])

    def fill_kwargs(self, **kwargs):
        for var, val in kwargs.items():
            self.setval(var, val)

    def assert_full(self):
        if self.missing_vars():
            raise TypeError('Missing settings: {}'.format(self.missing_vars()))

    def fill(self, *args, **kwargs):
        self.fill_kwargs(**kwargs)
        self.fill_arg(*args)
        self.assert_full()
        return self

    def setval(self, varname, value):
        if varname in self:
            self[varname]['value'] = value
        else:
            self[varname] = Variable(value=value)

    def missing_vars(self):
        return [x for x,y in self.items() if not y.is_filled()]