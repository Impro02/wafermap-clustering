# MODULES
import os
from pathlib import Path

# MODELS
from ..models.clustering_result import ClusteringResult


def write_baby_klarf(
    clustering_result: ClusteringResult,
    attribute: str,
    output_name: Path = None,
):
    if output_name is None:
        output_name = (
            Path(os.getcwd())
            / f"{clustering_result.lot_id}_{clustering_result.step_id}_{clustering_result.wafer_id}_clustered.000"
        )

    file_version = " ".join(str(clustering_result.file_version).split("."))

    defects = [
        get_defect_row(
            defect_id=clustered_defect.defect_id,
            bin=clustered_defect.bin,
            last_row=index == clustering_result.number_of_defects - 1,
        )
        for index, clustered_defect in enumerate(clustering_result.clustered_defects)
    ]

    with open(output_name, "w") as f:
        f.write(f"FileVersion {file_version};\n")
        f.write(f"ResultTimestamp {clustering_result.result_timestamp};\n")
        f.write(f'LotID "{clustering_result.lot_id}";\n')
        f.write(f'DeviceID "{clustering_result.device_id}";\n')
        f.write(f'StepID "{clustering_result.step_id}";\n')
        f.write(f'WaferID "{clustering_result.wafer_id}";\n')
        f.write(f"DefectRecordSpec 2 DEFECTID {attribute} ;\n")
        f.write(f"DefectList\n")
        f.write("".join(defects))
        f.write("EndOfFile;")


def get_defect_row(defect_id: int, bin: int, last_row: bool = False):
    row = f" {defect_id} {bin}"

    if last_row:
        row = f"{row};"

    return f"{row}\n"
