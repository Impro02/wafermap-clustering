from dataclasses import dataclass, field
from typing import List

from models.clustered_defect import ClusteredDefect


@dataclass
class ClusteringResult:
    result_timestamp: str
    lot_id: int
    step_id: str
    wafer_id: str
    clusters: int
    processing_timestamp: float
    clustered_defects: List[ClusteredDefect] = field(default=lambda: [])