# MODULES
import logging
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from collections import Counter

# UNITTEST
import unittest

# WAFERMAP_CLUSTERING
from wafermap_clustering.wafermap_clustering import Clustering
from wafermap_clustering.configs.config import (
    ClusteringMode,
    Config,
    KlarfFormat,
)

ASSETS_PATH: Path = Path(__file__).parent / "assets"
ASSETS_OUTPUT_PATH: Path = ASSETS_PATH / "clustering" / "output"


def setup_logger(name: str, directory: Path):
    logger = logging.getLogger(name=name)

    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Add a file handler to log messages to a file
        directory.mkdir(parents=True, exist_ok=True)

        time_rotating_handler = TimedRotatingFileHandler(
            filename=directory / f"{name}.log",
            when="midnight",
            interval=1,
            backupCount=10,
        )
        time_rotating_handler.setLevel(logging.INFO)
        time_rotating_handler.setFormatter(formatter)
        logger.addHandler(time_rotating_handler)

    return logger


class TestClustering(unittest.TestCase):
    def setUp(self) -> None:
        self.path_klarf_single_wafer_no_defect = ASSETS_PATH / "klarf_no_defect.000"
        self.path_klarf_single_wafer = ASSETS_PATH / "LAA_FAA_LAA-01.000"
        self.path_klarf_multi_wafers = ASSETS_PATH / "QUU_NUU.000"
        self.path_klarf_single_wafer_large_klarf = ASSETS_PATH / "LARGE_KLARF.000"

        self.config = Config(
            conf_path=ASSETS_PATH / "conf" / "config.json",
        )

        self.logger = setup_logger(
            name="clustering", directory=Path(self.config.directories.logs)
        )

    def assertFileEqual(self, first: Path, second: Path, ignore_rows: list[str]):
        with open(first, "r") as file1, open(second, "r") as file2:
            for line1, line2 in zip(file1, file2):
                if any(
                    line.lower().startswith(row.lower())
                    for row in ignore_rows
                    for line in [line1, line2]
                ):
                    continue

                self.assertEqual(line1, line2)

        return True

    def test_clustering_dbscan_single_wafer_no_defect(self):
        # GIVEN
        expected_summary = [
            {
                "result_timestamp": "01-01-20 00:00:00",
                "lot_id": "BOO",
                "step_id": "LOO",
                "wafer_id": "02",
                "clusters": 0,
                "clustering": {},
            }
        ]

        # WHEN
        clustering = Clustering(config=self.config)
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_single_wafer_no_defect,
        )

        summary = [
            {
                "result_timestamp": res.result_timestamp,
                "lot_id": res.lot_id,
                "step_id": res.step_id,
                "wafer_id": res.wafer_id,
                "clusters": res.clusters,
                "clustering": dict(
                    Counter([cluster.bin for cluster in res.clustered_defects])
                ),
            }
            for res in results
        ]

        # THEN
        self.assertEqual(summary, expected_summary)

    def test_clustering_dbscan_single_wafer(self):
        # GIVEN
        expected_summary = [
            {
                "result_timestamp": "01-01-20 00:00:00",
                "lot_id": "LAA",
                "step_id": "FAA",
                "wafer_id": "01",
                "clusters": 3,
                "clustering": {
                    -1: 13,
                    0: 10580,
                    1: 1670,
                },
            }
        ]

        # WHEN
        clustering = Clustering(config=self.config)
        tic = time.perf_counter()
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_single_wafer,
        )
        print(f"{time.perf_counter()-tic} s")

        summary = [
            {
                "result_timestamp": res.result_timestamp,
                "lot_id": res.lot_id,
                "step_id": res.step_id,
                "wafer_id": res.wafer_id,
                "clusters": res.clusters,
                "clustering": dict(
                    Counter([cluster.bin for cluster in res.clustered_defects])
                ),
            }
            for res in results
        ]

        # THEN
        self.assertEqual(summary, expected_summary)

    def test_clustering_dbscan_single_wafer_large_klarf(self):
        # GIVEN
        expected_summary = [
            {
                "result_timestamp": "01-01-20 00:00:00",
                "lot_id": "MOO",
                "step_id": "ZUU",
                "wafer_id": "04",
                "clusters": 8,
                "clustering": {
                    -1: 116,
                    0: 15883,
                    1: 3831,
                    2: 2342,
                    3: 7,
                    4: 4,
                    5: 4,
                    6: 3,
                },
            }
        ]

        # WHEN
        clustering = Clustering(config=self.config)
        tic = time.perf_counter()
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_single_wafer_large_klarf,
        )
        print(f"{time.perf_counter()-tic} s")

        summary = [
            {
                "result_timestamp": res.result_timestamp,
                "lot_id": res.lot_id,
                "step_id": res.step_id,
                "wafer_id": res.wafer_id,
                "clusters": res.clusters,
                "clustering": dict(
                    Counter([cluster.bin for cluster in res.clustered_defects])
                ),
            }
            for res in results
        ]

        # THEN
        self.assertEqual(summary, expected_summary)

    def test_clustering_hdbscan_single_wafer(self):
        # GIVEN
        expected_summary = [
            {
                "result_timestamp": "01-01-20 00:00:00",
                "lot_id": "LAA",
                "step_id": "FAA",
                "wafer_id": "01",
                "clusters": 3,
                "clustering": {
                    -1: 13,
                    0: 10580,
                    1: 1670,
                },
            }
        ]

        # WHEN
        clustering = Clustering(config=self.config)
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_single_wafer,
            output_directory=ASSETS_OUTPUT_PATH,
            klarf_format=KlarfFormat.FULL.value,
            clustering_mode=ClusteringMode.HDBSCAN.value,
        )

        summary = [
            {
                "result_timestamp": res.result_timestamp,
                "lot_id": res.lot_id,
                "step_id": res.step_id,
                "wafer_id": res.wafer_id,
                "clusters": res.clusters,
                "clustering": dict(
                    Counter([cluster.bin for cluster in res.clustered_defects])
                ),
            }
            for res in results
        ]

        # THEN
        self.assertEqual(summary, expected_summary)

    def test_clustering_dbscan_multi_wafers(self):
        # GIVEN
        expected_summary = [
            {
                "result_timestamp": "01-01-20 00:00:00",
                "lot_id": "QUU",
                "step_id": "NUU",
                "wafer_id": "02",
                "clusters": 6,
                "clustering": {-1: 12, 0: 22, 1: 3, 2: 4, 3: 11, 4: 4},
            },
            {
                "result_timestamp": "01-01-20 00:00:00",
                "lot_id": "QUU",
                "step_id": "NUU",
                "wafer_id": "06",
                "clusters": 3,
                "clustering": {
                    -1: 9,
                    0: 14,
                    1: 13,
                },
            },
            {
                "result_timestamp": "01-01-20 00:00:00",
                "lot_id": "QUU",
                "step_id": "NUU",
                "wafer_id": "01",
                "clusters": 8,
                "clustering": {
                    -1: 34,
                    0: 17,
                    1: 7,
                    2: 7,
                    3: 3,
                    4: 19,
                    5: 5,
                    6: 3,
                },
            },
        ]

        # WHEN
        clustering = Clustering(config=self.config)
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_multi_wafers,
            clustering_mode=ClusteringMode.DBSCAN.value,
        )

        summary = [
            {
                "result_timestamp": res.result_timestamp,
                "lot_id": res.lot_id,
                "step_id": res.step_id,
                "wafer_id": res.wafer_id,
                "clusters": res.clusters,
                "clustering": dict(
                    Counter(sorted([cluster.bin for cluster in res.clustered_defects]))
                ),
            }
            for res in results
        ]

        # THEN
        self.assertEqual(summary, expected_summary)

    def test_clustering_dbscan_no_defect_with_baby_klarf_returned(self):
        # GIVEN
        saved_klarf_paths = sorted(
            [ASSETS_PATH / "saved" / "klarf_baby" / "BOO_LOO_02_dbscan_no_defect.000"]
        )

        # WHEN
        clustering = Clustering(config=self.config)
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_single_wafer_no_defect,
            output_directory=ASSETS_OUTPUT_PATH,
            klarf_format=KlarfFormat.BABY.value,
        )
        results = sorted(results, key=lambda x: x.output_filename)

        # THEN
        self.assertEqual(len(results), len(saved_klarf_paths))
        for index, result in enumerate(results):
            self.assertFileEqual(
                saved_klarf_paths[index],
                result.output_filename,
                ignore_rows=["FileTimestamp"],
            )

    def test_clustering_dbscan_no_defect_with_full_klarf_returned(self):
        # GIVEN
        saved_klarf_paths = sorted(
            [ASSETS_PATH / "saved" / "klarf_full" / "klarf_no_defect_dbscan.000"]
        )

        # WHEN
        clustering = Clustering(config=self.config)
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_single_wafer_no_defect,
            output_directory=ASSETS_OUTPUT_PATH,
            klarf_format=KlarfFormat.FULL.value,
        )
        results = sorted(results, key=lambda x: x.output_filename)

        # THEN
        self.assertEqual(len(results), len(saved_klarf_paths))
        for index, result in enumerate(results):
            self.assertFileEqual(
                saved_klarf_paths[index],
                result.output_filename,
                ignore_rows=["FileTimestamp"],
            )

    def test_clustering_dbscan_multi_wafers_with_baby_klarf_returned(self):
        # GIVEN
        saved_klarf_paths = sorted(
            [
                ASSETS_PATH / "saved" / "klarf_baby" / "QUU_NUU_01_dbscan.000",
                ASSETS_PATH / "saved" / "klarf_baby" / "QUU_NUU_02_dbscan.000",
                ASSETS_PATH / "saved" / "klarf_baby" / "QUU_NUU_06_dbscan.000",
            ]
        )

        # WHEN
        clustering = Clustering(config=self.config)
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_multi_wafers,
            output_directory=ASSETS_OUTPUT_PATH,
            klarf_format=KlarfFormat.BABY.value,
        )
        results = sorted(results, key=lambda x: x.output_filename)

        # THEN
        self.assertEqual(len(results), len(saved_klarf_paths))
        for index, result in enumerate(results):
            self.assertFileEqual(
                saved_klarf_paths[index],
                result.output_filename,
                ignore_rows=["FileTimestamp"],
            )

    def test_clustering_dbscan_multi_wafers_with_full_klarf_returned(self):
        # GIVEN
        saved_klarf_path = ASSETS_PATH / "saved" / "klarf_full" / "QUU_NUU_dbscan.000"

        # WHEN
        clustering = Clustering(config=self.config)
        results = clustering.apply_from_klarf_path(
            logger=self.logger,
            klarf_path=self.path_klarf_multi_wafers,
            output_directory=ASSETS_OUTPUT_PATH,
            klarf_format=KlarfFormat.FULL.value,
        )
        results = sorted(results, key=lambda x: x.output_filename)

        # THEN
        for result in results:
            self.assertFileEqual(
                saved_klarf_path,
                result.output_filename,
                ignore_rows=["FileTimestamp"],
            )
