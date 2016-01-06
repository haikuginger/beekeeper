"""
Provides methods and classes that handle working with variables
"""

from functools import partial

def merge(var1, var2):
    """
    Take two copies of a variable and reconcile them. var1 is assumed
    to be the higher-level variable, and so will be overridden by var2
    where such becomes necessary.
    """
    out = {}
    out['value'] = var2.get('value', var1.get('value', None))
    out['mimetype'] = var2.get('mimetype', var1.get('mimetype', None))
    out['types'] = list(set(var1['types'] + var2['types']))
    out['optional'] = var2.get('optional', False)
    return Variable(**out)


class Variable(dict):

    """
    Like the Hive, the developer never touches the Variable object;
    it's basically a wrapper for the variables that the developer
    defines in the hive, and provides metadata methods.
    """

    def __init__(self, **kwargs):
        kwargs['types'] = kwargs.get('types', [])
        if not kwargs['types']:
            kwargs['types'].append(kwargs.get('type', 'url_param'))
        super().__init__(**kwargs)

    def is_filled(self):
        """
        Does the variable have a value, or is it optional?
        """
        if self.has_value() or self.get('optional', False):
            return True

    def has_type(self, var_type):
        """
        Does the variable have the given type?
        """
        if var_type in self.types():
            return True

    def has_value(self):
        """
        Does the variable have a value?
        """
        if self.get('value', None) is not None:
            return True

    def has_value_of_type(self, var_type):
        """
        Does the variable both have the given type and
        have a variable value we can use?
        """
        if self.has_value() and self.has_type(var_type):
            return True

    def types(self):
        """
        Return a list of the types the variable can be.
        """
        for each in self['types']:
            yield each

class Variables(dict):

    """
    Provides methods and storage for multiple variable objects
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.add(**kwargs)
        self.replacements = partial(self.vals, 'url_replacement')

    def types(self):
        """
        Return a list of all the variable types that exist in the
        Variables object.
        """
        output = set()
        for name, var in self.items():
            for var_type in var.types():
                output.add(var_type)
        return list(output)

    def vals(self, var_type):
        """
        Create a dictionary with name/value pairs listing the
        variables of a particular type that have a value.
        """
        return {x: y['value'] for x, y in self.items() if y.has_value_of_type(var_type)}

    def add(self, **kwargs):
        """
        Add additional single Variable objects to the Variables
        object.
        """
        for name, var in kwargs.items():
            if name in self:
                self[name] = merge(self[name], var)
            else:
                self[name] = Variable(**var)
        return self

    def fill_arg(self, *args):
        """
        If we get a single positional argument, and only a single
        variable needs to be filled, fill that variable with
        the value from that positional argument.
        """
        missing = self.missing_vars()
        if 1 == len(args) == len(missing):
            self.setval(missing[0], args[0])

    def fill_kwargs(self, **kwargs):
        """
        Fill empty variable objects by name with the values from
        any present keyword arguments.
        """
        for var, val in kwargs.items():
            self.setval(var, val)

    def assert_full(self):
        """
        Yell at the developer if the Variables object SHOULD be
        full, but ISN'T.
        """
        if self.missing_vars():
            raise TypeError('Missing settings: {}'.format(self.missing_vars()))

    def fill(self, *args, **kwargs):
        """
        Take args and kwargs and fill up any variables that
        don't have a value yet.
        """
        self.fill_kwargs(**kwargs)
        self.fill_arg(*args)
        self.assert_full()
        return self

    def setval(self, varname, value):
        """
        Set the value of the variable with the given name.
        """
        if varname in self:
            self[varname]['value'] = value
        else:
            self[varname] = Variable(value=value)

    def missing_vars(self):
        """
        List the names of the variables that don't have
        a value yet.
        """
        return [name for name, val in self.items() if not val.is_filled()]
