#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
github-indicator options

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import optparse
import os
import xdg.BaseDirectory


__version__ = (0, 0, 3)

ICON_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), 'icons'))

DATA_DIR = xdg.BaseDirectory.save_data_path('github-indicator')
CACHE_DIR = xdg.BaseDirectory.save_cache_path('github-indicator')
CONFIG_DIR = xdg.BaseDirectory.save_config_path('github-indicator')


parser = optparse.OptionParser(version='%prog ' + '.'.join(map(str, __version__)))
parser.add_option('-d', '--debug', action='store_true',
                  dest='debug', default=False,
                  help='Prints some debugging info')
parser.add_option('-s', '--status-icon', action='store_true',
                  dest='status_icon', default=False,
                  help='Use a gtk status icon instead of appindicator')
parser.add_option('-u', '--username', action='store',
                  dest='username', default=None,
                  help='GitHub username')
parser.add_option('-p', '--password', action='store',
                  dest='password', default=None,
                  help='GitHub password (won\'t be saved)')
parser.add_option('-t', '--update-time', action='store',
                  dest='update_time', default=60, type='int',
                  help='Checks for status updates after the specified amount of time [in seconds].')


def get_options():
    return parser.parse_args()
