from __future__ import unicode_literals

import unittest

import beekeeper.hive

hive_v5 = {
    "name": "test_hive",
    "versioning": {
        "version": 5,
        "other_versions": [
            {
                "version": 4,
                "location": "url_for_version_4"
            }
        ]
    }
}

hive_v4 = {
    "name": "test_hive",
    "versioning": {
        "version": 4,
        "other_versions": [
            {
                "version": 5,
                "location": "url_for_version_5"
            }
        ]
    }
}

hive_vfree = {
    "name": "test_hive",
}

def fake_download_as_json(url):
    hives = {
        "url_for_version_4": hive_v4,
        "url_for_version_5": hive_v5
    }
    return hives[url]

beekeeper.hive.download_as_json = fake_download_as_json

class HiveTest(unittest.TestCase):

    def setUp(self):
        self.hive = beekeeper.hive.Hive(**hive_v5)

    def test_get_version_url(self):
        self.assertEqual(self.hive.get_version_url(4), 'url_for_version_4')

    def test_get_nonexistent_version_url(self):
        with self.assertRaises(beekeeper.hive.VersionNotInHive):
            self.hive.get_version_url(6)

    def test_version(self):
        self.assertEqual(self.hive.version(), 5)

    def test_other_versions(self):
        self.assertEqual(
            self.hive.other_versions(),
            [
                {
                    "version": 4,
                    "location": "url_for_version_4"
                }
            ]
        )

    def test_from_version(self):
        self.assertEqual(
            self.hive.from_version(4),
            beekeeper.hive.Hive(**hive_v4)
        )

    def test_from_bad_version(self):
        with self.assertRaises(beekeeper.hive.VersionNotInHive):
            self.hive.from_version(10)

    def test_from_empty_version(self):
        self.assertEqual(
            self.hive.from_version(None),
            self.hive
        )

    def test_from_same_version(self):
        self.assertEqual(
            self.hive.from_version(5),
            self.hive
        )

    def test_no_hive_version(self):
        hive = beekeeper.hive.Hive(**hive_vfree)
        self.assertEqual(hive.version(), None)

    def test_available_versions_no_info(self):
        hive = beekeeper.hive.Hive(**hive_vfree)
        self.assertEqual(hive.other_versions(), [])

    def test_find_version_url_no_info(self):
        hive = beekeeper.hive.Hive(**hive_vfree)
        with self.assertRaises(beekeeper.hive.VersionNotInHive):
            hive.get_version_url(5)
