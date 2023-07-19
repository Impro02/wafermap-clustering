# MODULES
from dataclasses import dataclass


@dataclass
class ClusteringPerformance:
    clustering_timestamp: float = None
    output_timestamp: float = None

    def __repr__(self) -> str:
        returned_output_timestamp = (
            f"{self.output_timestamp=}s"
            if self.output_timestamp is not None
            else f"{self.output_timestamp=}"
        )
        return f"{self.clustering_timestamp=}s, {returned_output_timestamp}"
