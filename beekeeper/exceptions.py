class MissingHive(Exception):

    def __init__(self, location):
        self.location = location

    def __str__(self):
        return "Could not open hive at {}".format(self.location)

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
        if isinstance(self.obj, dict):
            for name, item in self.obj.items():
                if isinstance(item, dict):
                    if item:
                        output[name] = stwrapper('{...}')
                    else:
                        output[name] = stwrapper('{}')
                elif isinstance(item, list):
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

class HiveLoadedOverHTTP(Exception):

    def __init__(self, url, hive):
        self.url = url
        self.hive = hive

    def __str__(self):
        val = 'Hive was fetched insecurely over HTTP from URL {}'
        val = val.format(self.url)
        return val
