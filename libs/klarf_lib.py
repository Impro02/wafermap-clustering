# MODULES
import os
from typing import List
from pathlib import Path

# KLARF_READER
from klarf_reader.models.klarf_content import KlarfContent

# MODELS
from models.clustered_defect import ClusteredDefect


def write_clustered_baby_klarf(
    klarf_content: KlarfContent,
    clustered_defects: List[ClusteredDefect],
    output_path: Path = None,
):
    if output_path is None:
        output_path = Path(os.getcwd())

    output_file = (
        output_path
        / f"{klarf_content.lot_id}_{klarf_content.step_id}_{klarf_content.wafers[0].id}_clustered.000"
    )

    with open(output_file, "w") as f:
        defect_count = klarf_content.wafers[0].summary.number_of_defects

        f.write("FileVersion 1 2;\n")
        f.write(f"ResultTimestamp {klarf_content.result_timestamp};\n")
        f.write(f'LotID "{klarf_content.lot_id}";\n')
        f.write(f'DeviceID "{klarf_content.device_id}";\n')
        f.write(f'StepID "{klarf_content.step_id}";\n')
        f.write(f'WaferID "{klarf_content.wafers[0].id}";\n')
        f.write(f"DefectRecordSpec 2 DEFECTID DYN_CLUSTER_ID ;\n")
        f.write(f"DefectList\n")

        for index, defect in enumerate(klarf_content.wafers[0].defects):
            defect_bin = next(
                iter(
                    [
                        defect_point.bin
                        for defect_point in clustered_defects
                        if defect_point.defect_id == defect.id
                    ]
                )
            )
            row = f" {defect.id} {defect_bin}"
            if index == defect_count - 1:
                row = f"{row};"
            f.write(f"{row}\n")

        f.write("EndOfFile;")
