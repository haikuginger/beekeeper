class Variable(dict):

    def __init__(self, type, value=None, **kwargs):
        dict.__init__(self)
        self['type'] = type
        if value:
            self['value'] = value

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

    def add(self, **kwargs):
        for name, var in kwargs.items():
            self[name] = var
        return self

    def fill(self, check_complete=True, **kwargs):
        for var, val in kwargs.items():
            if var in self:
                self[var]['value'] = val
            else:
                self[var] = url_param(value=val)
        if check_complete:
            self.assert_full()
        return self

    def assert_full(self):
        missing = [x for x,y in self.items() if 'value' not in y]
        if len(missing):
            raise TypeError('Missing settings: {}'.format(missing))