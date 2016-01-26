class MissingHive(Exception):

    def __init__(self, location):
        self.location = location

    def __str__(self):
        return "Could not open hive at {}".format(location)

class VersionNotInHive(Exception):

    def __init__(self, version):
        self.version = version

    def __str__(self):
        return "Could not find location for version {}".format(self.version)

class TraversalError(Exception):

    def __init__(self, obj, key):
        self.obj = obj
        self.key = key

    def __str__(self):
        return 'Could not traverse object {} with key {}'.format(self.top_level(), repr(self.key))

    def top_level(self):
        output = {}
        if type(self.obj) is dict:
            for name, item in self.obj.items():
                if type(item) is dict:
                    if item:
                        output[name] = stwrapper('{...}')
                    else:
                        output[name] = stwrapper('{}')
                elif type(item) is list:
                    if item:
                        output[name] = stwrapper('[...]')
                    else:
                        output[name] = stwrapper('[]')
                else:
                    output[name] = item
            return output
        else:
            return self.obj

class stwrapper(str):

    def __repr__(self):
        return self
