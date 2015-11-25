class Variable(dict):

    def __init__(self, type, value=None, **kwargs):
        dict.__init__(self)
        self['type'] = type
        if value:
            self['value'] = value

class Header(Variable):

    def __init__(self, **kwargs):
        Variable.__init__(self, 'header', **kwargs)

class url_replacement(Variable):

    def __init__(self, **kwargs):
        Variable.__init__(self, 'url_replacement', **kwargs)

class url_param(Variable):

    def __init__(self, **kwargs):
        Variable.__init__(self, 'url_param', **kwargs)