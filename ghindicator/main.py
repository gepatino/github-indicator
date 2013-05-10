# -*- coding: utf-8 -*-
"""
Script to start the github-notifier app

Author: Gabriel Patiño <gepatino@gmail.com>
License: Do whatever you want
"""

import os
import logging

from ghindicator import options
from ghindicator import gui
from ghindicator import language
from ghindicator import log
from ghindicator import updaters


def run():
    updaters.updater_003_01()

    (opts, args) = options.get_options()
    logfile = os.path.join(options.CACHE_DIR, options.APPNAME + '.log')
    log.setup(options.APPNAME, log_level=opts.log_level, 
              log_type='file', file_name=logfile)
    logger = logging.getLogger(options.APPNAME)
    logger.critical(_('Starting github-indicator'))
    try:
        app = gui.get_app(opts)
        app.main()
    except KeyboardInterrupt:
        pass
    logger.critical(_('Closing github-indicator'))
    log.shutdown()
