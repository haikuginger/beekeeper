"""
Provides methods and classes that handle working with variables
"""

from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

from functools import partial
from keyword import iskeyword

DEFAULT_VARIABLE_TYPE = 'url_param'

def merge(var1, var2):
    """
    Take two copies of a variable and reconcile them. var1 is assumed
    to be the higher-level variable, and so will be overridden by var2
    where such becomes necessary.
    """
    out = {}
    out['value'] = var2.get('value', var1.get('value', None))
    out['mimetype'] = var2.get('mimetype', var1.get('mimetype', None))
    out['types'] = var2.get('types') + [x for x in var1.get('types') if x not in var2.get('types')]
    out['optional'] = var2.get('optional', var1.get('optional', False))
    out['filename'] = var2.get('filename', var2.get('filename', None))
    return Variable(**out)

class Variable(dict):

    """
    Like the Hive, the developer never touches the Variable object;
    it's basically a wrapper for the variables that the developer
    defines in the hive, and provides metadata methods.
    """

    def __init__(self, **kwargs):
        kwargs['types'] = kwargs.get('types', [])
        if not kwargs['types'] and kwargs.get('type', False):
            kwargs['types'].append(kwargs.pop('type'))
        dict.__init__(self, **kwargs)

    def is_filled(self):
        """
        Does the variable have a value, or is it optional?
        """
        if self.has_value() or self.get('optional', False):
            return True
        return False

    def has_type(self, var_type):
        """
        Does the variable have the given type? If not, are we looking
        for variables of the default type, and are no types
        defined for the variable in question?
        """
        if var_type in self.types():
            return True
        return False

    def has_value(self):
        """
        Does the variable have a value?
        """
        if self.value() is not None:
            return True
        return False

    def has_value_of_type(self, var_type):
        """
        Does the variable both have the given type and
        have a variable value we can use?
        """
        if self.has_value() and self.has_type(var_type):
            return True
        return False

    def types(self):
        """
        Return a list of the types the variable can be.
        """
        for each in self['types']:
            yield each
        if self.has_no_type():
            yield DEFAULT_VARIABLE_TYPE

    def has_no_type(self):
        """
        Does the Variable have a defined type?
        """
        if not self['types']:
            return True
        return False

    def value(self):
        """
        Get the value of the variable, if defined.
        """
        return self.get('value', None)

class Variables(dict):

    """
    Provides methods and storage for multiple variable objects
    """

    def __init__(self, **kwargs):
        dict.__init__(self)
        self.add(**kwargs)
        self.replacements = partial(self.vals, 'url_replacement')

    def required_names(self):
        """
        Get a list of the variables that we still need to fill in
        """
        return self.missing_vars()

    def optional_names(self):
        """
        Get a list of the variables that are defined, but not required
        """
        for name, var in self.items():
            if var.get('optional', False):
                yield name

    def required_namestring(self):
        """
        Compose a string showing the required variables (helper for the
        API printing function)
        """
        return ', '.join(self.required_names())

    def optional_namestring(self):
        """
        Compose a string showing the optional variables (helper for the
        API printing function)
        """
        opt_names = list(self.optional_names())
        if opt_names:
            return '[, {}]'.format(', '.join(opt_names))
        else:
            return ''

    def types(self):
        """
        Return a list of all the variable types that exist in the
        Variables object.
        """
        output = set()
        for _, var in self.items():
            for var_type in var.types():
                if self.vals(var_type):
                    output.add(var_type)
        return list(output)

    def vals(self, var_type):
        """
        Create a dictionary with name/value pairs listing the
        variables of a particular type that have a value.
        """
        return {x: y for x, y in self.items() if y.has_value_of_type(var_type)}

    def add(self, **kwargs):
        """
        Add additional single Variable objects to the Variables
        object.
        """
        for name, var in kwargs.items():
            if iskeyword(name):
                var['name'] = name
                name = '_' + name
            if name in self:
                self[name] = merge(self[name], Variable(**var))
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
            raise TypeError('Expected values for variables: {}'.format(self.missing_vars()))

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
