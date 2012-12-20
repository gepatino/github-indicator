# -*- coding: utf-8 -*-

"""Logging setup"""

import logging
import logging.handlers

try:
    import codecs
except ImportError:
    codecs = None


LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    }


class Formatter(logging.Formatter):
    """Formats log messages"""
    def format(self, record):
        msg = logging.Formatter.format(self, record)
        if type(msg) is unicode:
            msg = msg.encode('utf-8')
            if codecs:
                msg = codecs.BOM_UTF8 + msg
        return msg


def setup(appname, log_type=None, log_level=None,
          file_name=None, file_max_size=1e6, file_backups=10,
          syslog_address=None, syslog_port=None, syslog_facility=None):
    """Function to setup the logging according to the received options"""

    if log_type is None:
        # Disable logging
        logging.disable(logging.CRITICAL)
        return

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
        hdlr = logging.handlers.RotatingFileHandler(file_name, 'a', 
                                                    file_max_size, 
                                                    file_backups)
    else:
        # Default handler
        hdlr = None

    if hdlr is not None:
        fmt = '%(asctime)s %(name)s[%(process)d]: %(levelname)-8s %(message)s'
        formtr = Formatter(fmt)
        hdlr.setFormatter(formtr)
        logger = logging.getLogger(appname)
        logger.setLevel(LEVELS.get(log_level, logging.NOTSET))
        logger.addHandler(hdlr)


def shutdown():
    logging.shutdown()
