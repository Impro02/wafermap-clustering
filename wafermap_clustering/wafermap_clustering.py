# MODULES
import time
from pathlib import Path
from typing import List
from logging import Logger

# NUMPY
import numpy as np

# SCIKIT_LEARN
from sklearn.cluster import DBSCAN

# KLARF_READER
from klarf_reader.klarf import Klarf
from klarf_reader.utils import klarf_convert

from wafermap_clustering.configs.config import KlarfFormat

# MODELS
from .models.config import Config
from .models.clustered_defect import ClusteredDefect
from .models.clustering_result import ClusteringResult

# LIBS
from .libs import klarf_lib

# CONFIGS
from .configs.logging_config import setup_logger


class Clustering:
    def __init__(
        self, config: Config, logger: Logger = None, autocreate_logger: bool = False
    ) -> None:
        self.config = config

        self.logger = (
            setup_logger(platform=self.config.platform)
            if autocreate_logger and self.logger is None
            else logger
        )

    def apply(
        self,
        klarf_path: Path,
        output_path: Path = None,
        klarf_format=KlarfFormat.BABY.value,
    ) -> List[ClusteringResult]:

        klarf_content = Klarf.load_from_file(filepath=klarf_path)

        results: List[ClusteringResult] = []
        for index, wafer in enumerate(klarf_content.wafers):
            tic = time.time()

            single_klarf = klarf_convert.convert_to_single_klarf_content(
                klarf_content=klarf_content, wafer_index=index
            )

            defect_ids = np.array([defect.id for defect in wafer.defects])
            defect_points = np.array(
                [
                    (defect.point[0] / 1000, defect.point[1] / 1000)
                    for defect in wafer.defects
                ]
            )

            clustering = DBSCAN(
                eps=self.config.clustering.eps,
                min_samples=self.config.clustering.min_samples,
            ).fit(defect_points)

            clustering_values = np.column_stack((defect_ids, clustering.labels_))

            clusters = len(np.unique(clustering.labels_, axis=0))

            clustered_defects = [
                ClusteredDefect(
                    defect_id=defect_id,
                    bin=cluster_label,
                )
                for defect_id, cluster_label in clustering_values
            ]

            clustering_result = ClusteringResult(
                file_version=single_klarf.file_version,
                result_timestamp=single_klarf.result_timestamp,
                lot_id=single_klarf.lot_id,
                device_id=single_klarf.device_id,
                step_id=single_klarf.step_id,
                wafer_id=single_klarf.wafer.id,
                clusters=clusters,
                clustered_defects=clustered_defects,
            )

            match klarf_format:
                case KlarfFormat.BABY.value if output_path is not None:
                    klarf_lib.write_baby_klarf(
                        clustering_result=clustering_result,
                        attribute=self.config.attribute,
                        output_filename=output_path,
                    )
                case KlarfFormat.FULL.value if output_path is not None:
                    klarf_lib.write_full_klarf(
                        klarf_path=klarf_path,
                        clustering_result=clustering_result,
                        attribute=self.config.attribute,
                        output_filename=output_path,
                    )

            clustering_result.processing_timestamp = time.time() - tic

            results.append(clustering_result)

            if self.logger is not None:
                self.logger.info(
                    msg=f"({repr(clustering_result)}) was processed in {clustering_result.processing_timestamp} [{clusters=}]"
                )

        return results
