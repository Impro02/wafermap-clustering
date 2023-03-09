# MODULES
from dataclasses import dataclass


@dataclass
class ClusteringConfig:
    eps: int
    min_samples: int


@dataclass
class Config:
    platform: str
    attribute: str
    clustering: ClusteringConfig
