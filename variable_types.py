from functools import partial

def is_var(var):
    return isinstance(var, Variable)

class Variable(dict):

    def __init__(self, type, **kwargs):
        super().__init__(**kwargs)
        self['type'] = type

    def is_filled(self):
        if 'value' in self or ('optional' in self and self['optional']):
            return True
        return False

class header(Variable):

    def __init__(self, **kwargs):
        super().__init__('header', **kwargs)

class url_replacement(Variable):

    def __init__(self, **kwargs):
        super().__init__('url_replacement', **kwargs)

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
        self.data = partial(self.vals, 'data')

    def vals(self, var_type, final=False):
        if final:
            self.assert_full()
        return {x:y['value'] for x,y in self.items() if y['type']==var_type and 'value' in y}

    def populate(self, **kwargs):
        '''This needs thinking out. Goal is to unify .add and .fill, with
        ability to handle both variable declarations and settings at the same time.
        Order of operations for partials in Python should mean that the latest-filled
        copy of an argument will be used as part of kwargs. We do manually need to
        load in full declarations first so that plain assignments end up with the
        right type.'''
        self.add(**{n: val for n, val in kwargs.items() if is_var(val)})
        self.fill(**{n: val for n, val in kwargs.items() if not is_var(val)})

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