# MODULES
import os
from pathlib import Path
from typing import List

# MODELS
from ..models.clustering_result import ClusteringResult


def generate_output_file_name(output_name: str, clustering_result: ClusteringResult):
    if output_name is None:
        output_name = (
            Path(os.getcwd())
            / f"{clustering_result.lot_id}_{clustering_result.step_id}_{clustering_result.wafer_id}_clustered.000"
        )

    return output_name


def write_full_klarf(
    raw_content: List[str],
    clustering_result: ClusteringResult,
    attribute: str,
    output_filename: Path = None,
):
    output_filename = generate_output_file_name(
        output_name=output_filename, clustering_result=clustering_result
    )

    # Open a new file in write mode
    with open(output_filename, "w") as f:
        next_line_has_coords = False
        for line in raw_content:
            if line.lstrip().lower().startswith("defectrecordspec"):
                line_tmp = line.split(";")
                line_tmp = line_tmp[0].split(" ")

                line_tmp[1] = str(int(line_tmp[1]) + 1)
                line_tmp = f"{' '.join(line_tmp)}{attribute};\n"
                f.write(line_tmp)
                continue
            if line.lstrip().lower().startswith("defectlist") and not (
                line.rstrip().endswith(";")
            ):
                next_line_has_coords = True
                f.write(line)
                continue

            if next_line_has_coords:
                is_last_row = line.rstrip().endswith(";")

                defect_id = int(line.split()[0])

                bin = next(
                    (
                        cluster.bin
                        for cluster in clustering_result.clustered_defects
                        if cluster.defect_id == defect_id
                    ),
                    None,
                )

                next_line_has_coords = not is_last_row
                f.write(
                    create_full_defect_row(
                        original_row=line, bin=bin, last_row=is_last_row
                    )
                )

            else:
                # Write the original line to the new file
                f.write(line)


def write_baby_klarf(
    clustering_result: ClusteringResult,
    attribute: str,
    output_filename: Path = None,
):
    output_filename = generate_output_file_name(
        output_name=output_filename, clustering_result=clustering_result
    )

    file_version = " ".join(str(clustering_result.file_version).split("."))

    defects = [
        create_baby_defect_row(
            defect_id=clustered_defect.defect_id,
            bin=clustered_defect.bin,
            last_row=index == clustering_result.number_of_defects - 1,
        )
        for index, clustered_defect in enumerate(clustering_result.clustered_defects)
    ]

    with open(output_filename, "w") as f:
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


def create_baby_defect_row(defect_id: int, bin: int, last_row: bool = False):
    row = f" {defect_id} {bin}"

    if last_row:
        row = f"{row};"

    return f"{row}\n"


def create_full_defect_row(original_row: str, bin: int, last_row: bool = False):
    original_row_tmp = (
        original_row.split("\n") if not last_row else original_row.split(";\n")
    )
    row = f"{original_row_tmp[0]} {bin}"

    if last_row:
        row = f"{row};"

    return f"{row}\n"
