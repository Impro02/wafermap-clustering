# MODULES
import time
import numpy as np
from pathlib import Path
from typing import List
from sklearn.cluster import DBSCAN

# KLARF_READER
from klarf_reader.klarf import Klarf

# MODELS
from models.cluseting_config import ClusteringConfig
from models.clustered_defect import ClusteredDefect

# LIBS
from libs import klarf_lib


class Clustering:
    def __init__(self, config: ClusteringConfig) -> None:
        self.config = config

    def apply(
        self,
        klarf_path: Path,
        baby_klarf: bool = False,
    ) -> float:

        klarf_content = Klarf.load_from_file(filepath=klarf_path)

        for wafer in klarf_content.wafers:
            tic = time.time()

            defect_ids = [defect.id for defect in wafer.defects]
            defect_points = np.array(
                [
                    (defect.point[0] / 1000, defect.point[1] / 1000)
                    for defect in wafer.defects
                ]
            )

            clustering = DBSCAN(
                eps=self.config.eps, min_samples=self.config.min_samples
            ).fit(defect_points)

            clustering_values, clusters = np.column_stack(
                (np.array(defect_ids), clustering.labels_)
            ), np.unique(clustering.labels_, axis=0)

            defect_dict = {defect.id: defect for defect in wafer.defects}
            clustered_defects = {c: [] for c in clusters}
            for defect_id, cluster_label in clustering_values:
                if defect_id in defect_dict:
                    defect = defect_dict[defect_id]
                    cluster = clustered_defects[cluster_label]
                    cluster.append(
                        ClusteredDefect(
                            defect_id=defect.id,
                            bin=cluster_label,
                        )
                    )

            clustered_defect_points: List[ClusteredDefect] = [
                point for cluster in clustered_defects.values() for point in cluster
            ]

            if baby_klarf:
                klarf_lib.write_clustered_baby_klarf(
                    klarf_content=klarf_content,
                    clustered_defects=clustered_defect_points,
                    output_path=Path(self.config.output_path),
                )

            return time.time() - tic
