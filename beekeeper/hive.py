from .comms import download_as_json
import json

class Hive(dict):

    """
    The Hive class is invisible to the developer; it wraps the parsed JSON and
    provides methods for working with the information in it. Right now, most
    methods have to do with getting the JSON and parsing version information.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_file(cls, fname, version=None):
        """
        Create a Hive object based on JSON located in a local file.
        """
        return cls(**json.load(open(fname, 'r'))).from_version(version)

    @classmethod
    def from_url(cls, url, version=None):
        """
        Create a Hive object based on JSON located at a remote URL.
        """
        return cls(**download_as_json(url)).from_version(version)

    def from_version(self, version):
        """
        Create a Hive object based on the information in the object
        and the version passed into the method.
        """
        if not version or self['versioning']['version'] == version:
            return self
        else:
            return Hive.from_url(self.get_version_url(version))

    def get_version_url(self, version):
        """
        Retrieve the URL for the designated version of the hive.
        """
        for v in self['versioning']['previous_versions']:
            if version == v:
                return v['location']
        raise KeyError('Could not locate hive for version {}'.format(version))
