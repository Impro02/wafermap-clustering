# MODULES
import time
import re
from pathlib import Path
from typing import Any, Generator, List

# KLARF_READER
from klarf_reader.models.klarf_content import SingleKlarfContent, Defect

# MODELS
from ..models.clustering_result import ClusteringResult


def write_full_klarf(
    raw_klarf: Generator[str, Any, None],
    clustering_results: List[ClusteringResult],
    attribute: str,
    output_filename: Path,
) -> float:

    if output_filename is None:
        return

    tic = time.time()

    clustering_mapper = {
        item.wafer_id: {
            defect.defect_id: defect.bin for defect in item.clustered_defects
        }
        for item in clustering_results
    }

    next_row_has_coords = False
    with open(output_filename, "w") as f:
        for row in raw_klarf:
            if row.lstrip().lower().startswith("waferid"):
                wafer_id = row.split('"')[1]

            if row.lstrip().lower().startswith("defectrecordspec"):
                row_without_space = re.sub("[\s;]+", " ", row).strip()
                parameters = row_without_space.strip().split(" ")
                tmp_record = int(parameters[1]) + 1
                parameters[1] = str(tmp_record)
                last_param = parameters[-1]
                has_image_list = last_param.lower() == "imagelist"
                if has_image_list:
                    parameters.insert(-1, attribute)
                else:
                    parameters.append(attribute)
                dyn_cluster_id_index = parameters.index(attribute)
                parameters.append(";\n")
                row = " ".join(parameters)

            if row.lstrip().lower().startswith("defectlist") and not (
                row.rstrip().endswith(";")
            ):
                next_row_has_coords = True

            if next_row_has_coords:
                if row.startswith(" "):
                    row_without_space = re.sub("[\s;]+", " ", row).strip()
                    defect_parameters = row_without_space.rstrip().split(" ")

                    defect_id = int(defect_parameters[0])

                    dyn_cluster_id = str(
                        clustering_mapper.get(wafer_id, {}).get(defect_id)
                    )
                    if has_image_list:
                        defect_parameters.insert(
                            dyn_cluster_id_index - 2, dyn_cluster_id
                        )
                    else:
                        defect_parameters.append(dyn_cluster_id)

                    if row.rstrip().endswith(";"):
                        defect_parameters.append(";")

                    defect_parameters.insert(0, " ")
                    defect_parameters.append("\n")

                    row = " ".join(defect_parameters)

                if row.rstrip().endswith(";"):
                    next_row_has_coords = False

            f.write(row)

    return time.time() - tic


def write_baby_klarf(
    single_klarf: SingleKlarfContent,
    clustering_result: ClusteringResult,
    attribute: str,
    output_filename: Path,
) -> float:

    if output_filename is None:
        return

    tic = time.time()

    file_version = " ".join(str(single_klarf.file_version).split("."))

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
        f.write(f"ResultTimestamp {single_klarf.result_timestamp};\n")
        f.write(f'LotID "{single_klarf.lot_id}";\n')
        f.write(f'DeviceID "{single_klarf.device_id}";\n')
        f.write(f'StepID "{single_klarf.step_id}";\n')
        f.write(f'WaferID "{single_klarf.wafer.id}";\n')
        f.write(f"DefectRecordSpec 2 DEFECTID {attribute} ;\n")
        if len(defects) == 0:
            f.write(f"DefectList;\n")
        else:
            f.write(f"DefectList\n")
            f.write("".join(defects))
        f.write("EndOfFile;")

    return time.time() - tic


def create_baby_defect_row(
    defect_id: int,
    bin: int,
    last_row: bool = False,
):
    row = f" {defect_id} {bin}"

    if last_row:
        row = f"{row};"

    return f"{row}\n"


def create_defect_row(
    defect: Defect,
    bin: int,
    last_row: bool = False,
):
    row = f" {defect.id} {defect.x_rel:0.3f} {defect.y_rel:0.3f} {defect.x_index} {defect.y_index} {defect.x_size:0.3f} {defect.y_size:0.3f} {defect.area:0.3f} {defect.d_size:0.3f} {defect.class_number} {defect.test_id} {defect.cluster_number} {defect.roughbin} {defect.finebin} {defect.image_count} {bin}"

    if last_row:
        row = f"{row};"

    return f"{row}\n"


def create_sample_test_plan_row(
    indexes: tuple[int, int],
    last_row: bool = False,
):
    row = f" {indexes[0]} {indexes[1]}"

    if last_row:
        row = f"{row};"

    return f"{row}\n"
