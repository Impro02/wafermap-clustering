# MODULES
import json
from pathlib import Path

# MODELS
from models.cluseting_config import ClusteringConfig

# CORE
from clustering import Clustering

CONFIGS_CLUSTERING_PATH = Path("configs") / "config.json"


def load_config(filepath: Path):
    configs = None
    with open(filepath, encoding="utf-8") as json_data_file:
        try:
            configs = json.load(json_data_file)
        except Exception as ex:
            print(f"Configuration file {filepath} is invalid: {ex}")
            exit()

    return ClusteringConfig(
        attribute=configs["attribute"],
        eps=configs["clustering"]["eps"],
        min_samples=configs["clustering"]["min_samples"],
    )


if __name__ == "__main__":
    CONFIGS = load_config(filepath=CONFIGS_CLUSTERING_PATH)

    clustering = Clustering(config=CONFIGS)
    clustering.apply(
        klarf_path=Path("tests") / "assets" / "J305PGM_8625.000",
        baby_klarf=True,
        show=True,
    )

    print("fin")
