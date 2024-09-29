from datetime import datetime
import logging

from pytz import utc

"""
TODO: Figure out to do logging and where to store logs
This is an example I came across to help get started
"""


def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    formatter.converter = utcTimeZone
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


"""
Converts local timezone to UTC in order to have a common server time for timestamps
"""
def utcTimeZone(*args):
    utc_dt = utc.localize(datetime.utcnow())
    return utc_dt.timetuple()


# For testing
if __name__ == "__main__":
    logger = get_module_logger(__name__)
    logger.info("Testing 1 2 3")
