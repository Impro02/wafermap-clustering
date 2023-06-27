# MODULES
import time
from pathlib import Path
import datetime

# KLARF_READER
from klarf_reader.models.klarf_content import SingleKlarfContent, Defect

# MODELS
from ..models.clustering_result import ClusteringResult


def write_full_klarf(
    single_klarf: SingleKlarfContent,
    clustering_result: ClusteringResult,
    attribute: str,
    output_filename: Path,
) -> float:

    tic = time.time()

    file_version = " ".join(str(single_klarf.file_version).split("."))

    defect_dict = {
        defect.defect_id: defect.bin for defect in clustering_result.clustered_defects
    }

    defect_rows = [
        create_defect_row(
            defect=defect,
            bin=defect_dict.get(defect.id),
            last_row=index == clustering_result.number_of_defects - 1,
        )
        for index, defect in enumerate(single_klarf.wafer.defects)
    ]

    sample_test_plan = list(
        zip(
            single_klarf.sample_plan_test.x,
            single_klarf.sample_plan_test.y,
        )
    )

    num_sample_test_plan = len(sample_test_plan)

    sample_test_plan_rows = [
        create_sample_test_plan_row(
            indexes=indexes,
            last_row=index == num_sample_test_plan - 1,
        )
        for index, indexes in enumerate(sample_test_plan)
    ]

    with open(output_filename, "w") as f:
        f.write(f"FileVersion {file_version};\n")
        f.write(
            f"FileTimestamp {datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S')};\n"
        )
        f.write(
            f'InspectionStationID "{single_klarf.inspection_station_id.mfg}" "{single_klarf.inspection_station_id.model}" "{single_klarf.inspection_station_id.id}";\n'
        )
        f.write(f"SampleType {single_klarf.sample_type};\n")
        f.write(f"ResultTimestamp {single_klarf.result_timestamp};\n")
        f.write(f'LotID "{single_klarf.lot_id}";\n')
        f.write(f"SampleSize 1 {single_klarf.sample_size};\n")
        f.write(f'DeviceID "{single_klarf.device_id}";\n')
        f.write(
            f'SetupID "{single_klarf.setup_id.name}" {single_klarf.setup_id.date};\n'
        )
        f.write(f'StepID "{single_klarf.step_id}";\n')
        f.write(
            f'SampleOrientationMarkType "{single_klarf.sample_orientation_mark_type}";\n'
        )
        f.write(
            f'OrientationMarkLocation "{single_klarf.orientation_mark_location}";\n'
        )
        f.write(
            f"DiePitch {single_klarf.die_pitch.x:0.10e} {single_klarf.die_pitch.y:0.10e};\n"
        )
        f.write(
            f"DieOrigin {single_klarf.wafer.die_origin.x:0.10e} {single_klarf.wafer.die_origin.y:0.10e};\n"
        )
        f.write(f'WaferID "{single_klarf.wafer.id}";\n')
        f.write(f"Slot {single_klarf.wafer.slot};\n")
        f.write(
            f"SampleCenterLocation {single_klarf.wafer.sample_center_location.x:0.10e} {single_klarf.wafer.sample_center_location.y:0.10e};\n"
        )
        f.write(f"SampleTestPlan {num_sample_test_plan}\n")
        f.write("".join(sample_test_plan_rows))
        for test in single_klarf.wafer.tests:
            f.write(f"InspectionTest {test.id}\n")
            f.write(f"AreaPerTest {test.area:0.10e}\n")
        f.write(
            f"DefectRecordSpec 14 DEFECTID XREL YREL XINDEX YINDEX XSIZE YSIZE DEFECTAREA DSIZE CLASSNUMBER TEST CLUSTERNUMBER ROUGHBINNUMBER FINEBINNUMBER IMAGECOUNT {attribute} ;\n"
        )
        f.write(f"DefectList\n")
        f.write("".join(defect_rows))
        f.write("EndOfFile;")

    return time.time() - tic


def write_baby_klarf(
    single_klarf: SingleKlarfContent,
    clustering_result: ClusteringResult,
    attribute: str,
    output_filename: Path,
) -> float:

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
