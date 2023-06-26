# MODULES
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logger(name: str, directory: Path):
    logger = logging.getLogger(name=name)

    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Add a file handler to log messages to a file
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
