#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to start the github-notifier app

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import os

from ghindicator import options
from ghindicator import gui
from ghindicator import log


def run():
    (opts, args) = options.get_options()
    logfile = os.path.join(options.CACHE_DIR, 'github-indicator.log')
    log.setup('github-indicator', log_level=opts.log_level, 
              log_type='file', file_name=logfile)

    try:
        app = gui.get_app(opts)
        app.main()
    except KeyboardInterrupt:
        pass
