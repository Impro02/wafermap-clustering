# CONFIGS
from configs.config import CONFIGS
from configs import logging_config

LOGGER = logging_config.LOGGER

if __name__ == "__main__":
    from libs.pipeline_lib import PipeLine

    pipeline = PipeLine(config=CONFIGS)
    pipeline.start()
