# MODULES
import json
import platform
import os
from pathlib import Path

# MODELS
from ..models.config import Config, ClusteringConfig


def load_config(filepath: Path):
    root_config, clustering_config = {}, {}
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as json_data_file:
            try:
                root_config: dict = json.load(json_data_file)
                clustering_config = root_config.get("clustering", {})
            except Exception as ex:
                print(f"Configuration file {filepath} is invalid: {ex}")
                exit()

    return Config(
        platform=platform.system().lower(),
        attribute=root_config.get("attribute", None),
        clustering=ClusteringConfig(
            eps=clustering_config.get("eps", None),
            min_samples=clustering_config.get("min_samples", None),
        ),
    )


CONFIGS_CLUSTERING_PATH = Path().parent / "config.json"
CONFIGS = load_config(filepath=CONFIGS_CLUSTERING_PATH)
