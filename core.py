# CONFIGS
from configs.config import CONFIGS
from configs.logging_config import LOGGER

LOGGER = LOGGER

if __name__ == "__main__":
    from pipeline import PipeLine

    pipeline = PipeLine(config=CONFIGS)
    pipeline.start()
