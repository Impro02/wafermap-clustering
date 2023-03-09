# MODULES
from dataclasses import dataclass, field
from typing import List

# MODELS
from models.clustered_defect import ClusteredDefect


@dataclass
class ClusteringResult:
    file_version: float
    result_timestamp: str
    lot_id: int
    device_id: str
    step_id: str
    wafer_id: str
    clusters: int
    clustered_defects: List[ClusteredDefect] = field(default=lambda: [])
    processing_timestamp: float = field(default=lambda: None)

    @property
    def number_of_defects(self):
        return len(self.clustered_defects)
