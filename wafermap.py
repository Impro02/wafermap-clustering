import json
from pathlib import Path
import time
import numpy as np
from sklearn.cluster import DBSCAN

from klarf_reader.klarf import Klarf
from wafermap_plot.wafermap import WaferMapPlot
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

defect_ids = [defect.id for defect in content.wafers[0].defects]
defect_points = [
    (defect.point[0] / 1000, defect.point[1] / 1000)
    for defect in content.wafers[0].defects
]

wafermap = WaferMapPlot.plot(defect_points=defect_points)
wafermap.show()


clustering = DBSCAN(eps=configs.eps, min_samples=configs.min_samples).fit(defect_points)

tic = time.time()
clustering_values, number_of_cluster = np.column_stack(
    (np.array(defect_ids), clustering.labels_)
), np.unique(clustering.labels_, axis=0)
tac = time.time()
