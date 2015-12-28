from functools import partial
from urllib.parse import urlencode
from parsers import encode

def is_var(var):
    return isinstance(var, Variable)

class Variable(dict):

    def __init__(self, type, **kwargs):
        super().__init__(**kwargs)
        self['type'] = type

    def is_filled(self):
        if 'value' in self or self.get('optional', False):
            return True
        return False

class url_param(Variable):

    def __init__(self, **kwargs):
        super().__init__('url_param', **kwargs)

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
                raise TypeError("Only one data-type variable can have a value")
        return None

    def vals(self, var_type, final=False):
        if final:
            self.assert_full()
        return {x:y['value'] for x,y in self.items() if y['type']==var_type and 'value' in y}

    def add(self, **kwargs):
        for name, var in kwargs.items():
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
            self[varname] = url_param(value=value)

    def missing_vars(self):
        return [x for x,y in self.items() if not y.is_filled()]