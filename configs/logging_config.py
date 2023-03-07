import sys
import logging

from configs.config import CONFIGS


def setup_logger(platform: str):

    match platform.lower():
        case "windows":
            logger = logging.getLogger(name="clustering")
            logger.setLevel(logging.INFO)

            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)

            logger.addHandler(handler)
        case _:
            logging.basicConfig(
                filename="clustering.log",
                level=logging.INFO,
            )

            logger = logging.getLogger()

    return logger

LOGGER = setup_logger(platform=CONFIGS.platform)
