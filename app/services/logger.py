import logging
import sys


LOGGER_NAME = "EMA_ALERT_BOT"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    logger.addHandler(console)

    return logger