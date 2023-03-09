# MODULES
import json
import platform
from pathlib import Path

# MODELS
from models.config import Config, ClusteringConfig, MailingConfig, PathConfig


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

    return Config(
        time_sleep=configs["time_sleep"],
        platform=platform_system,
        attribute=configs["attribute"],
        path=PathConfig(input=input_path, output=output_path, error=error_path),
        clustering=ClusteringConfig(
            eps=configs["clustering"]["eps"],
            min_samples=configs["clustering"]["min_samples"],
        ),
        mailing=MailingConfig(
            host=configs["mailing"]["host"],
            port=configs["mailing"]["port"],
            sender=configs["mailing"]["sender"],
            receiver=configs["mailing"]["receiver"],
        ),
    )


CONFIGS_CLUSTERING_PATH = Path("configs") / "config.json"
CONFIGS = load_config(filepath=CONFIGS_CLUSTERING_PATH)
