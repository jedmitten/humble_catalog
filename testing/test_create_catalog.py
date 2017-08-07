"""
test_publisher_data.py from hb_library_catalog
Created: 8/7/2017
"""
# Stdlib
from __future__ import print_function

import logging
import os
import unittest

# Custom Code
from utils import project_root
from create_catalog import assign_type, get_publishers

log = logging.getLogger(__name__)
__author__ = 'jed.mitten'
__version__ = '0.0.1'

PUBS = {
    "ebooks": {
        "display_name": "eBooks",
        "publishers": [
            "no starch press",
        ]
    },
    "android_apps": {
        "display_name": "Android Apps",
        "publishers": [
            "inxile entertainment"
        ]
    },
    "pc_games": {
        "display_name": "PC Games",
        "publishers": [
            "electronic arts",
        ]
    }
}


class TestingBase(unittest.TestCase):
    @staticmethod
    def get_asset_fp(fn, dir_mod=''):
        target_dir = project_root()
        target_dir = os.path.join(target_dir, dir_mod)
        asset_fp = os.path.join(target_dir, fn)
        return asset_fp


class TestPublishers(TestingBase):
    def test_get_publishers(self):
        fp = self.get_asset_fp('publishers.json')
        pubs = get_publishers(fp)
        self.assertIsInstance(pubs, dict)
        for key in PUBS:
            self.assertIn(key, pubs.keys())

    def test_assign_type_good(self):
        expected_type = 'eBooks'
        inputs = ['No Starch Press',
                  'no starch press',
                  'NO stArCh PreSs',
                  ]
        for i in inputs:
            found_type = assign_type(i, PUBS)
            self.assertEqual(expected_type, found_type)

    def test_assign_type_bad(self):
        expected_type = ''
        inputs = ['No such book',
                  'No such program',
                  'I have no idea what you\'re talking about',
                  ]
        for i in inputs:
            found_type = assign_type(i, PUBS)
            self.assertEqual(expected_type, found_type)
