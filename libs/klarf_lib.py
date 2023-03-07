# MODULES
import os
from typing import List
from pathlib import Path

# KLARF_READER
from klarf_reader.models.klarf_content import SingleKlarfContent

# MODELS
from models.clustered_defect import ClusteredDefect


def write_clustered_baby_klarf(
    klarf_content: SingleKlarfContent,
    clustered_defects: List[ClusteredDefect],
    output_name: Path = None,
):
    if output_name is None:
        output_name = (
            Path(os.getcwd())
            / f"{klarf_content.lot_id}_{klarf_content.step_id}_{klarf_content.wafer.id}_clustered.000"
        )

    file_version = " ".join(str(klarf_content.file_version).split("."))
    defect_count = klarf_content.wafer.summary.number_of_defects

    defects = [
        get_defect_row(
            defect_id=clustered_defect.defect_id,
            bin=clustered_defect.bin,
            last_row=index == defect_count - 1,
        )
        for index, clustered_defect in enumerate(clustered_defects)
    ]

    with open(output_name, "w") as f:
        f.write(f"FileVersion {file_version};\n")
        f.write(f"ResultTimestamp {klarf_content.result_timestamp};\n")
        f.write(f'LotID "{klarf_content.lot_id}";\n')
        f.write(f'DeviceID "{klarf_content.device_id}";\n')
        f.write(f'StepID "{klarf_content.step_id}";\n')
        f.write(f'WaferID "{klarf_content.wafer.id}";\n')
        f.write(f"DefectRecordSpec 2 DEFECTID DYN_CLUSTER_ID ;\n")
        f.write(f"DefectList\n")
        f.write("".join(defects))
        f.write("EndOfFile;")


def get_defect_row(defect_id: int, bin: int, last_row: bool = False):
    row = f" {defect_id} {bin}"

    if last_row:
        row = f"{row};"

    return f"{row}\n"
