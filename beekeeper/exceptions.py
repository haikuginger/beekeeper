from beekeeper.comms import ResponseException

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
