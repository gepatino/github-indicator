# -*- coding: utf-8 -*-
"""
github-indicator options

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import optparse
import os
import xdg.BaseDirectory

from ghindicator import language


__version__ = (0, 0, 4)

# Hack to fix a missing function in my version of xdg
if not hasattr(xdg.BaseDirectory, 'save_cache_path'):
    def save_cache_path(resource):
        path = os.path.join('/', xdg.BaseDirectory.xdg_cache_home, resource)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    xdg.BaseDirectory.save_cache_path = save_cache_path


APPNAME = 'github-indicator'
ICON_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), 'icons'))

DATA_DIR = xdg.BaseDirectory.save_data_path(APPNAME)
CONFIG_DIR = xdg.BaseDirectory.save_config_path(APPNAME)
CACHE_DIR = xdg.BaseDirectory.save_cache_path(APPNAME)


parser = optparse.OptionParser(version='%prog ' + '.'.join(map(str, __version__)))
parser.add_option('-s', '--status-icon', action='store_true',
                  dest='status_icon', default=False,
                  help=_('Use a gtk status icon instead of appindicator'))
parser.add_option('-u', '--username', action='store',
                  dest='username', default=None,
                  help=_('GitHub username'))
parser.add_option('-p', '--password', action='store',
                  dest='password', default=None,
                  help=_('GitHub password (won\'t be saved)'))
parser.add_option('-t', '--update-time', action='store',
                  dest='update_time', default=60, type='int',
                  help=_('Checks for status updates after the specified amount of time [in seconds].'))
parser.add_option('-l', '--log-level', action='store',
                  dest='log_level', default='error',
                  help=_('Sets logging level to one of [debug|info|warning|error|critical]'))


def get_options():
    return parser.parse_args()
