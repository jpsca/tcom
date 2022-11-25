import logging


LOGGER_NAME = "tcom"
LOGGER_LEVEL = logging.DEBUG
# LOGGER_LEVEL = logging.INFO

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOGGER_LEVEL)
