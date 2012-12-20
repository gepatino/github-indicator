# -*- coding: utf-8 -*-
""" Functions to update from one version to another. """

import os
import shutil

from ghindicator import options


def updater_003_01():
    old_dir = os.path.realpath(os.path.join(os.path.expanduser('~'), '.github-indicator'))
    events_file = 'last_notified_event'
    src_file = os.path.join(old_dir, events_file)
    dst_file = os.path.join(options.CACHE_DIR, events_file)
    if os.path.isfile(src_file):
        if not os.path.isfile(dst_file):
            shutil.move(src_file, dst_file)
    if os.path.isdir(old_dir):
        shutil.rmtree(old_dir, ignore_errors=True)
