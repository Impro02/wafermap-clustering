# MODULES
import getpass
import json
import os
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from typing import Annotated, List, Optional
import annotated_types

# PYDANTIC
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    PositiveFloat,
    PositiveInt,
    NonNegativeInt,
)


class KlarfFormat(Enum):
    BABY = "baby"
    FULL = "full"


class ClusteringMode(Enum):
    DBSCAN = "dbscan"
    HDBSCAN = "hdbscan"


class DBSCANAlgorithm(Enum):
    auto = "auto"
    ball_tree = "ball_tree"
    kd_tree = "kd_tree"
    brute = "brute"


class EpsilonValues(BaseModel):
    min_points: NonNegativeInt
    max_points: Optional[PositiveInt] = Field(default=None)
    epsilon: PositiveFloat

    @model_validator(mode="after")
    def validate_range(self):
        if self.max_points is not None and self.min_points > self.max_points:
            raise ValueError("min_points should be less than or equal to max_points")

        return self


class _DBSCANBaseConfig(BaseModel):
    epsilon_values: Annotated[List[EpsilonValues], annotated_types.Len(min_length=1)]

    @field_validator("epsilon_values")
    @classmethod
    def validate_epsilon_values(cls, epsilon_values: List[EpsilonValues]):
        last_item = epsilon_values[-1]

        if last_item.max_points is not None:
            raise ValueError("The last epsilon_values should not have max_points")

        for index, epsilon_value in enumerate(epsilon_values):
            if index == 0:
                tmp_min_points = epsilon_value.min_points
                tmp_max_points = epsilon_value.max_points

            if epsilon_value.min_points < tmp_min_points:
                raise ValueError("min_points should be in ascending order")

            if (
                epsilon_value.max_points is not None
                and epsilon_value.max_points < tmp_max_points
            ):
                raise ValueError("max_points should be in ascending order")

            if index > 0 and epsilon_value.min_points != tmp_max_points:
                raise ValueError(
                    "min_points should be equals than the previous max_points"
                )

            tmp_min_points = epsilon_value.min_points
            tmp_max_points = epsilon_value.max_points

        return epsilon_values


class DBSCANConfig(_DBSCANBaseConfig):
    algorithm: DBSCANAlgorithm = DBSCANAlgorithm.auto
    min_samples: int


class HDBSCANConfig(_DBSCANBaseConfig):
    min_samples: int
    min_cluster_size: int


class ClusteringConfig(BaseModel):
    dbscan: DBSCANConfig
    hdbscan: HDBSCANConfig


class DirectoryConfig(BaseModel):
    root: str
    home: str
    logs: str
    tmp: str


@dataclass
class Config:
    conf_path: str

    project_name: str = field(init=False)
    directories: DirectoryConfig = field(init=False)
    attribute: str = field(init=False)
    clustering: ClusteringConfig = field(init=False)

    def __post_init__(self):
        self.raw_data = self.__load_config(file_path=self.conf_path)
        self.raw_data = self.__replace_variables(self.raw_data)

        directories_config = self.raw_data.get("directories", {})
        clustering_config = self.raw_data.get("clustering", {})
        dbscan_config = clustering_config.get("dbscan", {})
        hdbscan_config = clustering_config.get("hdbscan", {})

        self.project_name = self.raw_data.get("project_name")
        self.directories = DirectoryConfig(
            root=directories_config.get("root"),
            home=os.path.expanduser("~"),
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

        replaced_config: dict = json.loads(json.dumps(config))

        def replace_variable(value):
            if isinstance(value, str):
                return (
                    value.replace("{{root}}", config["directories"]["root"])
                    .replace("{{home}}", os.path.expanduser("~"))
                    .replace("{{project_name}}", config["project_name"])
                    .replace("{{user}}", getpass.getuser())
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
