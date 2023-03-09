# MODULES
import time
import os
from pathlib import Path
from typing import List

# NUMPY
import numpy as np

# SCIKIT_LEARN
from sklearn.cluster import DBSCAN

# KLARF_READER
from klarf_reader.klarf import Klarf
from klarf_reader.utils import klarf_convert

# MODELS
from models.config import ClusteringConfig
from models.clustered_defect import ClusteredDefect
from models.clustering_result import ClusteringResult

# LIBS
from libs import klarf_lib

# CORE
from core import LOGGER


class Clustering:
    def __init__(self, config: ClusteringConfig) -> None:
        self.config = config

    def apply(
        self,
        klarf_path: Path,
        output_path: Path = None,
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
                eps=self.config.eps,
                min_samples=self.config.min_samples,
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

            if output_path is not None:
                klarf_lib.write_baby_klarf(
                    clustering_result=clustering_result,
                    output_name=output_path,
                )

            tac = time.time() - tic

            clustering_result.processing_timestamp = tac

            results.append(clustering_result)

            LOGGER.info(
                msg=f"(lot={single_klarf.lot_id}, step_id={single_klarf.step_id}, wafer_id={single_klarf.wafer.id}, inspection_time={single_klarf.result_timestamp}) was processed in {tac} [{clusters=}]"
            )

        return results
