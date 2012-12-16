#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to start the github-notifier app

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import os

from ghindicator.options import WORKING_DIR
from ghindicator.options import CACHE_DIR
from ghindicator.options import get_options
from ghindicator.gui import get_app


def run():
    (options, args) = get_options()
    for d in (WORKING_DIR, CACHE_DIR):
        if not os.path.exists(d):
            os.makedirs(d)
    try:
        app = get_app(options)
        app.main()
    except KeyboardInterrupt:
        pass
