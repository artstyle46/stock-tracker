import logging
import sys

from config import get_settings

settings = get_settings()


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(settings.LOGGING_LEVEL)

    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d : %(message)s"
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
