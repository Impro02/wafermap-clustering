# MODULES
import time
import os
import shutil
from pathlib import Path

# CONFIGS
from configs import config, logging_config

# CORE
from clustering import Clustering

CONFIGS_CLUSTERING_PATH = Path("configs") / "config.json"
CONFIGS = config.load_config(filepath=CONFIGS_CLUSTERING_PATH)

LOGGER = logging_config.setup_logger(platform=CONFIGS.platform)


def start():
    clustering = Clustering(config=CONFIGS)
    while True:
        time.sleep(5)

        klarf_paths = sorted(
            [
                Path(os.path.join(CONFIGS.input_path, f))
                for f in os.listdir(CONFIGS.input_path)
                if os.path.isfile(os.path.join(CONFIGS.input_path, f))
            ],
            key=lambda x: os.path.getmtime(os.path.join(CONFIGS.input_path, x)),
        )

        nbr_klarfs = len(klarf_paths)

        if not nbr_klarfs == 0:
            for klarf_path in klarf_paths:
                klarf = str(klarf_path)
                try:
                    size = os.path.getsize(klarf_path)

                    # wait until the file size stops changing
                    while True:
                        time.sleep(1)  # wait 1 second before checking again
                        new_size = os.path.getsize(klarf_path)
                        if new_size == size:
                            break
                        size = new_size

                    timestamp = clustering.apply(
                        klarf_path=klarf_path,
                        baby_klarf=True,
                    )

                    if os.path.exists(klarf_path):
                        os.remove(klarf_path)

                    LOGGER.info(
                        msg=f"{klarf=} was processed successfully in {timestamp}s"
                    )
                except Exception as ex:
                    shutil.move(
                        src=klarf_path,
                        dst=os.path.join(
                            CONFIGS.error_path, os.path.basename(klarf_path)
                        ),
                    )

                    LOGGER.critical(
                        msg=f"{klarf=} processing failed, moved to {CONFIGS.error_path}",
                        exc_info=ex,
                    )


if __name__ == "__main__":
    start()
