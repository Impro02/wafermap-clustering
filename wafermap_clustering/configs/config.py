# MODULES
import json
import os
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field


class KlarfFormat(Enum):
    BABY = "baby"
    FULL = "full"


class ClusteringMode(Enum):
    DBSCAN = "dbscan"
    HDBSCAN = "hdbscan"


@dataclass
class DBSCANConfig:
    min_samples: int
    eps: int


@dataclass
class HDBSCANConfig:
    min_samples: int
    min_cluster_size: int


@dataclass
class ClusteringConfig:
    dbscan: DBSCANConfig
    hdbscan: HDBSCANConfig


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
