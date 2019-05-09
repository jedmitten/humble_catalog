"""
utils.py from hb_library_catalog
Created: 8/7/2017
"""
# Stdlib
from __future__ import print_function
import logging
import os
import sys

# Third Party code
# Custom Code
log = logging.getLogger(__name__)
__author__ = 'jed.mitten'
__version__ = '0.0.1'


def project_root():
    root_dir = os.path.dirname(__file__)
    # if this file changes location, the following must be uncommented and changed
    # root_dir = os.path.join(root_path, '.')
    return os.path.abspath(root_dir)
