# MODULES
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import sys
import logging

# CONFIG
from ..configs.config import CONFIGS


def setup_logger(name: str):
    logger = logging.getLogger(name=name)

    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Add a stream handler to log messages to stdout
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # Add a file handler to log messages to a file
        directory = Path(CONFIGS.directories.logs)
        directory.mkdir(parents=True, exist_ok=True)

        time_rotating_handler = TimedRotatingFileHandler(
            filename=directory / f"{name}.log",
            when="midnight",
            interval=1,
            backupCount=10,
        )
        time_rotating_handler.setLevel(logging.INFO)
        time_rotating_handler.setFormatter(formatter)
        logger.addHandler(time_rotating_handler)

    return logger
