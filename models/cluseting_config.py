from dataclasses import dataclass


@dataclass
class ClusteringConfig:
    platform: str
    attribute: str
    input_path: str
    output_path: str
    error_path: str
    eps: int
    min_samples: int
