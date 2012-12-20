# -*- coding: utf-8 -*-

"""Logging setup

"""

import logging
import logging.handlers

try:
    import codecs
except ImportError:
    codecs = None


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL,
          'none': None}


class Formatter(logging.Formatter):
    """Formats log messages"""
    def format(self, record):
        msg = logging.Formatter.format(self, record)
        if type(msg) is unicode:
            msg = msg.encode('utf-8')
            if codecs:
                msg = codecs.BOM_UTF8 + msg
        return msg


def setup(appname, log_type=None, log_level=None, console_level=None,
            file_name=None, file_max_size=1e6, file_backups=10,
            syslog_address=None, syslog_port=None, syslog_facility=None):
    """Function to setup the logging according to the received options"""

    if log_type is None:
        # Disable logging
        logging.disable(logging.CRITICAL)
        return

    fmt = str(appname) + '[%(process)d]: %(message)s'

    if log_type == 'syslog':
        kwargs = {}
        if syslog_address is not None:
            if syslog_port is not None:
                kwargs['address'] = (syslog_address, syslog_port)
            else:
                kwargs['address'] = syslog_address
        if syslog_facility is not None:
            kwargs['facility'] = syslog_facility
        hdlr = logging.handlers.SysLogHandler(**kwargs)
    elif log_type == 'file':
        if not file_name:
            file_name = '/tmp/%s.log' % appname
        fmt = '%(asctime)s ' + fmt
        hdlr = logging.handlers.RotatingFileHandler(file_name, 'a', 
                                                    file_max_size, 
                                                    file_backups)
    else:
        # Default handler
        hdlr = None

    if hdlr is not None:
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        ### Console
        ##lvl_cons = LEVELS.get(console_level, logging.NOTSET)
        ##if lvl_cons is None:
        ##    logger.handlers = []
        ##else:
        ##    logger.handlers[0].setLevel(lvl_cons)

        # Syslog / File
        formtr = Formatter(fmt)
        hdlr.setFormatter(formtr)
        lvl = LEVELS.get(log_level, logging.NOTSET)
        hdlr.setLevel(lvl)
        logger.addHandler(hdlr)
