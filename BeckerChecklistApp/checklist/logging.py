import logging


def get_logger():
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    return logger
