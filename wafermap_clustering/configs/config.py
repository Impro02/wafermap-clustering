# MODULES
import json
import platform
import os
from enum import Enum
from pathlib import Path

# MODELS
from ..models.config import Config, ClusteringConfig, DBSCANConfig, HDBSCANConfig


class KlarfFormat(Enum):
    BABY = "baby"
    FULL = "full"


class ClusteringMode(Enum):
    DBSCAN = "dbscan"
    HDBSCAN = "hdbscan"


def load_config(filepath: Path):
    root_config, clustering_config, dbscan_config, hdbscan_config = {}, {}, {}, {}
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as json_data_file:
            try:
                root_config: dict = json.load(json_data_file)
                clustering_config = root_config.get("clustering", {})
                dbscan_config = clustering_config.get("dbscan", {})
                hdbscan_config = clustering_config.get("hdbscan", {})
            except Exception as ex:
                print(f"Configuration file {filepath} is invalid: {ex}")
                exit()

    return Config(
        platform=platform.system().lower(),
        attribute=root_config.get("attribute", None),
        clustering=ClusteringConfig(
            dbscan=DBSCANConfig(
                min_samples=dbscan_config.get("min_samples", None),
                eps=dbscan_config.get("eps", None),
            ),
            hdbscan=HDBSCANConfig(
                min_samples=hdbscan_config.get("min_samples", None),
                min_cluster_size=hdbscan_config.get("eps", None),
            ),
        ),
    )


CONFIGS_CLUSTERING_PATH = Path().parent / "config.json"
CONFIGS = load_config(filepath=CONFIGS_CLUSTERING_PATH)
