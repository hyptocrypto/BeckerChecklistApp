import logging


def get_logger():
    # Configure the logging module
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    # Send the logs to the appropriate streams
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    return logger
