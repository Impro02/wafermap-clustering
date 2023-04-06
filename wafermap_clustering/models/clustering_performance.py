# MODULES
from dataclasses import dataclass, field


@dataclass
class ClusteringPerformance:
    clustering_timestamp: float = field(default=lambda: None)
    output_timestamp: float = field(default=lambda: None)

    def __repr__(self) -> str:
        returned_output_timestamp = (
            f"{self.output_timestamp=}s"
            if self.output_timestamp is not None
            else f"{self.output_timestamp=}"
        )
        return f"{self.clustering_timestamp=}s, {returned_output_timestamp}"
