import utils
import json

class Hive(dict):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_file(cls, fname, version=None):
        return cls(**json.load(open(fname, 'r'))).from_version(version)

    @classmethod
    def from_url(cls, url, version=None):
        return cls(**utils.download_as_json(url)).from_version(version)

    def from_version(self, version):
        if self['versioning']['version'] == version or not version:
            return self
        else:
            return Hive(**utils.download_as_json(self.get_version_url(version)))

    def get_version_url(self, version):
        for v in self['versioning']['previous_versions']:
            if version == v:
                return v['location']
        raise KeyError('Could not locate hive for version {}'.format(version))
