# MODULES
import json
import platform
import os
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field

# MODELS
from ..models.config import Config, ClusteringConfig, DBSCANConfig, HDBSCANConfig


class KlarfFormat(Enum):
    BABY = "baby"
    FULL = "full"


class ClusteringMode(Enum):
    DBSCAN = "dbscan"
    HDBSCAN = "hdbscan"


@dataclass
class DirectoryConfig:
    root: str
    home: str
    logs: str
    tmp: str


@dataclass
class Config:
    platform: str
    conf_path: str

    project_name: str = field(init=False)
    directories: DirectoryConfig = field(init=False)
    attribute: str = field(init=False)
    clustering: ClusteringConfig = field(init=False)

    def __post_init__(self):
        self.raw_data = self.__load_config(file_path=self.conf_path)
        self.raw_data = self.__replace_variables(self.raw_data)

        platform_config = self.raw_data.get("platforms", {}).get(self.platform, {})
        directories_config = self.raw_data.get("directories", {})
        clustering_config = self.raw_data.get("clustering", {})
        dbscan_config = clustering_config.get("dbscan", {})
        hdbscan_config = clustering_config.get("hdbscan", {})

        self.project_name = self.raw_data.get("project_name")
        self.directories = DirectoryConfig(
            root=platform_config.get("root"),
            home=platform_config.get("home"),
            logs=directories_config.get("logs"),
            tmp=directories_config.get("tmp"),
        )
        self.attribute = self.raw_data.get("attribute")

        self.clustering = ClusteringConfig(
            dbscan=DBSCANConfig(**dbscan_config),
            hdbscan=HDBSCANConfig(**hdbscan_config),
        )

    def __load_config(self, file_path: Path) -> dict:
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)
        return data

    def __replace_variables(self, config: dict):
        platform = config.get("platforms", {}).get(self.platform)
        if platform is None:
            return None

        replaced_config: dict = json.loads(json.dumps(config))

        def replace_variable(value):
            if isinstance(value, str):
                return (
                    value.replace("{{root}}", platform["root"])
                    .replace("{{home}}", platform["home"])
                    .replace("{{project_name}}", config["project_name"])
                    .replace("{{user}}", os.getlogin())
                    .replace("{{project}}", os.path.abspath(os.getcwd()))
                )
            return value

        def traverse(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        traverse(value)
                    else:
                        obj[key] = replace_variable(value)
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    if isinstance(value, (dict, list)):
                        traverse(value)
                    else:
                        obj[i] = replace_variable(value)

        traverse(replaced_config)
        return replaced_config


"""
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
"""

# CONFIGS_CLUSTERING_PATH = Path().parent / "config.json"
# CONFIGS = load_config(filepath=CONFIGS_CLUSTERING_PATH)


CONFIGS = Config(
    platform=platform.system().lower(),
    conf_path=Path(__file__).parent / "config.json",
)
