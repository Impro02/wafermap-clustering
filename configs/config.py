# MODULES
import json
import platform
from pathlib import Path

# MODELS
from models.cluseting_config import ClusteringConfig


def load_config(filepath: Path):
    configs = None
    with open(filepath, encoding="utf-8") as json_data_file:
        try:
            configs = json.load(json_data_file)
        except Exception as ex:
            print(f"Configuration file {filepath} is invalid: {ex}")
            exit()

    platform_system = platform.system().lower()
    if platform_system in configs["platforms"]:
        input_path = configs["platforms"][platform_system]["input"]
        output_path = configs["platforms"][platform_system]["output"]
        error_path = configs["platforms"][platform_system]["error"]
    else:
        input_path = "/data/clustering/tmp"
        output_path = "/data/clustering/output"
        error_path = "/data/clustering/error"

    return ClusteringConfig(
        platform=platform_system,
        input_path=input_path,
        output_path=output_path,
        error_path=error_path,
        attribute=configs["attribute"],
        eps=configs["clustering"]["eps"],
        min_samples=configs["clustering"]["min_samples"],
    )
