import json
from pathlib import Path
import time
from typing import List
import numpy as np
from sklearn.cluster import DBSCAN

from klarf_reader.klarf import Klarf
from wafermap_plot.wafermap import WaferMapPlot
from wafermap_plot.models.defect_point import DefectPoint
from models.cluseting_config import ClusteringConfig


def load_config(filepath: Path):
    configs = None
    with open(filepath, encoding="utf-8") as json_data_file:
        try:
            configs = json.load(json_data_file)
        except Exception as ex:
            print(f"Configuration file {filepath} is invalid: {ex}")
            exit()

    return ClusteringConfig(eps=configs["eps"], min_samples=configs["min_samples"])


CONFIGS_CLUSTERING_PATH = Path("configs") / "clustering.json"

configs = load_config(filepath=CONFIGS_CLUSTERING_PATH)

path = Path("tests") / "assets" / "J247LFS_8625.000"

content = Klarf.load_from_file(filepath=path)

for wafer in content.wafers:
    tic = time.time()

    defect_ids = [defect.id for defect in wafer.defects]
    defect_points = [
        (defect.point[0] / 1000, defect.point[1] / 1000) for defect in wafer.defects
    ]

    clustering = DBSCAN(eps=configs.eps, min_samples=configs.min_samples).fit(
        defect_points
    )

    clustering_values, clusters = np.column_stack(
        (np.array(defect_ids), clustering.labels_)
    ), np.unique(clustering.labels_, axis=0)

    clustered_defect_points: List[DefectPoint] = []
    for cluster in clusters:
        tmp_defect_id = [cd[0] for cd in clustering_values if cd[1] == cluster]
        clustered_defect_points = [
            *clustered_defect_points,
            *[
                DefectPoint(
                    defect_id=defect.id,
                    point=(defect.point[0] / 1000, defect.point[1] / 1000),
                    bin=cluster,
                )
                for defect in wafer.defects
                if defect.id in tmp_defect_id
            ],
        ]

    wafermap = WaferMapPlot.plot(defect_points=clustered_defect_points)
    wafermap.show()

    tac = time.time()
