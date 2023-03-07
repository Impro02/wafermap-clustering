# MODULES
import time
import os
import shutil
from pathlib import Path

# MODELS
from models.config import Config

# CLUSTERING
from clustering import Clustering

# UTILS
from utils import mailing

# CONFIGS
from core import LOGGER, CONFIGS


class PipeLine:
    def __init__(self, config: Config) -> None:
        self.config = config

    def start(self):
        clustering = Clustering(config=self.config)
        while True:
            time.sleep(5)

            klarf_paths = sorted(
                [
                    Path(os.path.join(self.config.path.input, f))
                    for f in os.listdir(self.config.path.input)
                    if os.path.isfile(os.path.join(self.config.path.input, f))
                ],
                key=lambda x: os.path.getmtime(os.path.join(self.config.path.input, x)),
            )

            nbr_klarfs = len(klarf_paths)

            if not nbr_klarfs == 0:
                for klarf_path in klarf_paths:
                    klarf = os.path.basename(klarf_path)

                    try:
                        size = os.path.getsize(klarf_path)

                        # wait until the file size stops changing
                        while True:
                            time.sleep(1)  # wait 1 second before checking again
                            new_size = os.path.getsize(klarf_path)
                            if new_size == size:
                                break
                            size = new_size

                        clustering.apply(
                            klarf_path=klarf_path,
                            baby_klarf=True,
                        )

                        if os.path.exists(klarf_path):
                            os.remove(klarf_path)

                    except Exception as ex:
                        shutil.move(
                            src=klarf_path,
                            dst=os.path.join(
                                self.config.path.error, os.path.basename(klarf_path)
                            ),
                        )

                        message_error = f"{klarf=} processing failed, moved to {self.config.path.error}"

                        html = f"""\
                            <html>
                                <body>
                                    <p>{message_error}</p>
                                </body>
                            </html>
                        """

                        mailing.send_mail(
                            sender=CONFIGS.mailing.sender,
                            receiver=CONFIGS.mailing.reveiver,
                            subject=f"Clustering - Error on {klarf}",
                            msg_html=html,
                        )

                        LOGGER.critical(
                            msg=message_error,
                            exc_info=ex,
                        )
