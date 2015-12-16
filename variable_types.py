from functools import partial

class Variable(dict):

    def __init__(self, type, value=None, **kwargs):
        dict.__init__(self)
        self['type'] = type
        if value:
            self['value'] = value

    def is_filled(self):
        if 'value' in self or self['optional']:
            return True
        return False

class header(Variable):

    def __init__(self, **kwargs):
        Variable.__init__(self, 'header', **kwargs)

class url_replacement(Variable):

    def __init__(self, **kwargs):
        Variable.__init__(self, 'url_replacement', **kwargs)

class url_param(Variable):

    def __init__(self, **kwargs):
        Variable.__init__(self, 'url_param', **kwargs)

class Variables(dict):

    def __init__(self, **kwargs):
        dict.__init__(self)
        self.add(**kwargs)
        self.headers = partial(self.vals, 'header')
        self.replacements = partial(self.vals, 'url_replacement')
        self.params = partial(self.vals, 'url_param')

    def vals(self, var_type):
        return {x:y['value'] for x,y in self.items() if y['type']==var_type}

    def add(self, **kwargs):
        for name, var in kwargs.items():
            self[name] = var
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

    def fill(self, *args, full=True, **kwargs):
        self.fill_kwargs(**kwargs)
        self.fill_arg(*args)
        if full:
            self.assert_full()
        return self

    def setval(self, varname, value):
        if varname in self:
            self[varname]['value'] = value
        else:
            self[varname] = url_param(value=value)

    def missing_vars(self):
        return [x for x,y in self.items() if y.is_filled()]