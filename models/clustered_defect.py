# MODULES
from dataclasses import dataclass


@dataclass
class ClusteredDefect:
    defect_id: int
    bin: int = -1
