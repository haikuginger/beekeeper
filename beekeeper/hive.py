"""
Provides the Hive class to work with JSON hive files, both remotely
retrieved and opened from a local file
"""
from __future__ import absolute_import, division
from __future__ import unicode_literals, print_function

import json

from beekeeper.comms import download_as_json, ResponseException
from beekeeper.exceptions import MissingHive, VersionNotInHive

class Hive(dict):

    """
    The Hive class is invisible to the developer; it wraps the parsed JSON and
    provides methods for working with the information in it. Right now, most
    methods have to do with getting the JSON and parsing version information.
    """

    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    @classmethod
    def from_file(cls, fname, version=None):
        """
        Create a Hive object based on JSON located in a local file.
        """
        if os.path.exists(fname):
            return cls(**json.load(open(fname, 'r'))).from_version(version)
        else:
            raise MissingHive(fname)

    @classmethod
    def from_url(cls, url, version=None):
        """
        Create a Hive object based on JSON located at a remote URL.
        """
        try:
            return cls(**download_as_json(url)).from_version(version)
        except ResponseException:
            raise MissingHive(url)

    def from_version(self, version):
        """
        Create a Hive object based on the information in the object
        and the version passed into the method.
        """
        if version is None or self.version() == version:
            return self
        else:
            return Hive.from_url(self.get_version_url(version))

    def get_version_url(self, version):
        """
        Retrieve the URL for the designated version of the hive.
        """
        for each_version in self.other_versions():
            if version == each_version['version'] and 'location' in each_version:
                return each_version.get('location')
        raise VersionNotInHive(version)

    def version(self):
        """
        Retrieve the current hive's version, if present.
        """
        return self.get('versioning', {}).get('version', None)

    def other_versions(self):
        """
        Generate a list of other versions in the hive.
        """
        return self.get('versioning', {}).get('previous_versions', [])
