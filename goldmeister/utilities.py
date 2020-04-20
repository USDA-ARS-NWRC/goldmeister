import logging
import logging.config
import coloredlogs

def get_logger(name, level='DEBUG'):
    """
    Retrieve the logger with colored logs in it.
    """
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
    })
    fmt = fmt = '%(name)s %(levelname)s %(message)s'
    log = logging.getLogger(name)
    coloredlogs.install(fmt=fmt, level=level.upper(), logger=log)

    return log
