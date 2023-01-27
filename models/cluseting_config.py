

from dataclasses import dataclass


@dataclass
class ClusteringConfig:
    eps: int
    min_samples: int