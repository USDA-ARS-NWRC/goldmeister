import logging
import logging.config
import coloredlogs

def get_logger(name, level='DEBUG'):
    """
    Retrieve the logger with colored logs in it.
    """
    # logging.config.dictConfig({
    #     'version': 1,
    #     'disable_existing_loggers': True,
    # })
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
    })
    log = logging.getLogger(__name__)

    fmt = '%(name)s %(levelname)s %(message)s'
    coloredlogs.install(fmt=fmt, level=level.upper(), logger=log)

    return log
