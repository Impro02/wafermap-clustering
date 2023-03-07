# MODULES
import time
import os
import shutil
from pathlib import Path

# MODELS
from models.cluseting_config import ClusteringConfig

#CLUSTERING
from clustering import Clustering

# CONFIGS
from core import LOGGER

class PipeLine():

    def __init__(self, config: ClusteringConfig) -> None:
        self.config = config


    def start(self):
        clustering = Clustering(config=self.config)
        while True:
            time.sleep(5)

            klarf_paths = sorted(
                [
                    Path(os.path.join(self.config.input_path, f))
                    for f in os.listdir(self.config.input_path)
                    if os.path.isfile(os.path.join(self.config.input_path, f))
                ],
                key=lambda x: os.path.getmtime(os.path.join(self.config.input_path, x)),
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
                                self.config.error_path, os.path.basename(klarf_path)
                            ),
                        )

                        LOGGER.critical(
                            msg=f"{klarf=} processing failed, moved to {self.config.error_path}",
                            exc_info=ex,
                        )