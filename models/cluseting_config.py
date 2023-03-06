

from dataclasses import dataclass


@dataclass
class ClusteringConfig:
    attribute: str
    eps: int
    min_samples: int