# MODULES
import time
from pathlib import Path
from typing import List
from logging import Logger

# NUMPY
import numpy as np

# SCIKIT_LEARN
from sklearn.cluster import DBSCAN

# HDBSCAN
from hdbscan import HDBSCAN

# KLARF_READER
from klarf_reader.klarf import Klarf
from klarf_reader.utils import klarf_convert

from wafermap_clustering.configs.config import ClusteringMode, KlarfFormat
from wafermap_clustering.models.clustering_performance import ClusteringPerformance

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
            setup_logger(name="clustering", path=Path(__file__).parent)
            if autocreate_logger and logger is None
            else logger
        )

    def apply(
        self,
        klarf_path: Path,
        output_path: Path = None,
        klarf_format=KlarfFormat.BABY.value,
        clustering_mode=ClusteringMode.DBSCAN.value,
    ) -> List[ClusteringResult]:

        klarf_content, raw_content = Klarf.load_from_file_with_raw_content(
            filepath=klarf_path
        )

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

            match clustering_mode:
                case ClusteringMode.DBSCAN.value:
                    clustering = DBSCAN(
                        eps=self.config.clustering.dbscan.eps,
                        min_samples=self.config.clustering.dbscan.min_samples,
                    )
                    labels = clustering.fit_predict(defect_points)
                case ClusteringMode.HDBSCAN.value:
                    hdbscan = HDBSCAN(
                        min_samples=self.config.clustering.hdbscan.min_samples,
                        min_cluster_size=self.config.clustering.hdbscan.min_cluster_size,
                    )
                    labels = hdbscan.fit_predict(defect_points)

            clustering_values = np.column_stack((defect_ids, labels))
            clusters = len(np.unique(labels, axis=0))

            clustered_defects = [
                ClusteredDefect(
                    defect_id=defect_id,
                    bin=cluster_label,
                )
                for defect_id, cluster_label in clustering_values
            ]

            clustering_timestamp = time.time() - tic

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

            output_timestamp = None
            match klarf_format:
                case KlarfFormat.BABY.value if output_path is not None:
                    output_timestamp = klarf_lib.write_baby_klarf(
                        clustering_result=clustering_result,
                        attribute=self.config.attribute,
                        output_filename=output_path,
                    )
                case KlarfFormat.FULL.value if output_path is not None:
                    output_timestamp = klarf_lib.write_full_klarf(
                        raw_content=raw_content,
                        clustering_result=clustering_result,
                        attribute=self.config.attribute,
                        output_filename=output_path,
                    )

            clustering_result.performance = ClusteringPerformance(
                clustering_timestamp=round(clustering_timestamp, 3),
                output_timestamp=round(output_timestamp, 3)
                if output_timestamp is not None
                else None,
            )

            results.append(clustering_result)

            if self.logger is not None:
                self.logger.info(
                    msg=f"({repr(clustering_result)}) was sucessfully processed [defects={len(defect_ids)}, {clusters=}] with ({repr(clustering_result.performance)}) "
                )

        return results
