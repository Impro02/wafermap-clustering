# MODULES
from dataclasses import dataclass


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
class Config:
    platform: str
    attribute: str
    clustering: ClusteringConfig
