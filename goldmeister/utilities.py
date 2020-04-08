import logging
import coloredlogs

def get_logger(name, level='DEBUG'):
    """
    Retrieve the logger with colored logs in it.
    """

    fmt = fmt = '%(name)s %(levelname)s %(message)s'
    log = logging.getLogger(name)
    coloredlogs.install(fmt=fmt, level=level.upper(), logger=log)
    return log
