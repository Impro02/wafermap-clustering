# MODULES
from dataclasses import dataclass, field
from typing import List
from pathlib import Path

from wafermap_clustering.models.clustering_performance import ClusteringPerformance

# MODELS
from ..models.clustered_defect import ClusteredDefect


@dataclass
class ClusteringResult:
    file_version: float
    result_timestamp: str
    lot_id: int
    device_id: str
    step_id: str
    wafer_id: str
    inspection_tool: str
    clusters: int
    clustered_defects: List[ClusteredDefect]
    number_of_defects: int
    performance: ClusteringPerformance = None
    output_filename: Path = field(default_factory=lambda: None)

    def __repr__(self) -> str:
        return f"{self.lot_id=}, {self.step_id=}, {self.wafer_id=}, {self.inspection_tool}, {self.result_timestamp=}"
