# MODULES
import time
import os
from pathlib import Path

# NUMPY
import numpy as np

# SCIKIT_LEARN
from sklearn.cluster import DBSCAN

# KLARF_READER
from klarf_reader.klarf import Klarf
from klarf_reader.utils import klarf_convert

# MODELS
from models.cluseting_config import ClusteringConfig
from models.clustered_defect import ClusteredDefect

# LIBS
from libs import klarf_lib

# CONFIGS
from core import LOGGER


class Clustering:
    def __init__(self, config: ClusteringConfig) -> None:
        self.config = config

    def apply(
        self,
        klarf_path: Path,
        baby_klarf: bool = False,
    ) -> float:

        klarf_content = Klarf.load_from_file(filepath=klarf_path)

        klarf_basename = os.path.basename(klarf_path)
        klarf_name, klarf_extension = os.path.splitext(klarf_basename)

        tic = time.time()
        for index, wafer in enumerate(klarf_content.wafers):
            sub_tic = time.time()

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
                eps=self.config.eps, min_samples=self.config.min_samples
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
            LOGGER.info(
                msg=f"(lot={single_klarf.lot_id}, step_id={single_klarf.step_id}, wafer_id={single_klarf.wafer.id}, inspection_time={single_klarf.result_timestamp}) was processed in {time.time() - sub_tic} [{clusters=}]"
            )

            if baby_klarf:
                klarf_lib.write_clustered_baby_klarf(
                    klarf_content=single_klarf,
                    clustered_defects=clustered_defects,
                    output_name=Path(self.config.output_path)
                    / f"{klarf_name}_clustered{klarf_extension}",
                )

        return time.time() - tic
