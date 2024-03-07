# MODULES
import time
from pathlib import Path
from typing import Any, List, Tuple, Generator
from logging import Logger

# NUMPY
import numpy as np

# SKLEARN
from sklearn.cluster import HDBSCAN, DBSCAN

# KLARF_READER
from klarf_reader.klarf import Klarf, KlarfContent
from klarf_reader.utils import klarf_convert

# MODELS
from .models.clustered_defect import ClusteredDefect
from .models.clustering_performance import ClusteringPerformance
from .models.clustering_result import ClusteringResult

# LIBS
from .libs import klarf_lib

# CONFIGS
from .configs.config import ClusteringMode, Config, KlarfFormat


class Clustering:
    def __init__(
        self,
        config: Config,
    ) -> None:
        self.config = config

    def _find_eps(self, algorithm: ClusteringMode, nbr_defects: int) -> float:
        if algorithm == ClusteringMode.DBSCAN:
            epsilon_values = self.config.clustering.dbscan.epsilon_values
        elif algorithm == ClusteringMode.HDBSCAN:
            epsilon_values = self.config.clustering.hdbscan.epsilon_values
        else:
            raise ValueError(f"{algorithm=} is not supported")

        for epsilon_value in epsilon_values:
            lower_bound, upper_bound = (
                epsilon_value.min_points,
                epsilon_value.max_points,
            )
            if lower_bound <= nbr_defects and (
                upper_bound is None or nbr_defects < upper_bound
            ):
                return epsilon_value.epsilon

        raise ValueError(f"Could not find epsilon value for {nbr_defects=}")

    def apply_from_content(
        self,
        logger: Logger,
        content: Tuple[KlarfContent, Generator[str, Any, None]],
        output_directory: Path = None,
        original_klarf_name: str = None,
        original_klarf_extension: str = None,
        klarf_format=KlarfFormat.BABY.value,
        clustering_mode=ClusteringMode.DBSCAN.value,
    ):
        klarf_content, raw_content = content

        logger.info(f"Prepare to cluster {len(klarf_content.wafers)} wafer(s)")

        results: List[ClusteringResult] = []
        for index, _ in enumerate(klarf_content.wafers):
            tic = time.time()

            single_klarf = klarf_convert.convert_to_single_klarf_content(
                klarf_content=klarf_content, wafer_index=index
            )

            lot = single_klarf.lot_id
            wafer_id = single_klarf.wafer.id

            item_repr = {"lot": lot, "wafer_id": wafer_id}

            defects = {
                defect.id: [point / 1000 for point in defect.point]
                for defect in single_klarf.wafer.defects
            }

            defect_ids = np.array(list(defects.keys()))
            nbr_defects = len(defects)

            if nbr_defects == 0:
                clusters = 0
                clustered_defects = []
                clustering_timestamp = 0

                logger.info(f"{item_repr} does not have any defect")
            else:
                logger.info(
                    f"Starting clustering process for {item_repr} on {nbr_defects} defect(s)"
                )

                np_defect_points = np.array(
                    list(defects.values()),
                )

                match clustering_mode:
                    case ClusteringMode.DBSCAN.value:
                        clustering = DBSCAN(
                            eps=self._find_eps(
                                algorithm=ClusteringMode.DBSCAN,
                                nbr_defects=nbr_defects,
                            ),
                            min_samples=self.config.clustering.dbscan.min_samples,
                            algorithm=self.config.clustering.dbscan.algorithm.value,
                        )
                    case ClusteringMode.HDBSCAN.value:
                        clustering = HDBSCAN(
                            min_cluster_size=self.config.clustering.hdbscan.min_cluster_size,
                            min_samples=self.config.clustering.hdbscan.min_samples,
                            cluster_selection_epsilon=self._find_eps(
                                algorithm=ClusteringMode.HDBSCAN,
                                nbr_defects=nbr_defects,
                            ),
                        )
                    case _:
                        raise ValueError(f"{clustering_mode=} is not supported")

                labels = clustering.fit_predict(np_defect_points)

                clustering_values = np.column_stack((defect_ids, labels))
                clusters = len(np.unique(labels, axis=0))

                clustered_defects = [
                    ClusteredDefect(
                        defect_id=defect_id,
                        bin=cluster_label,
                    )
                    for defect_id, cluster_label in clustering_values
                ]

                clustering_timestamp = time.time() - tic

            clustering_result = ClusteringResult(
                file_version=single_klarf.file_version,
                result_timestamp=single_klarf.result_timestamp,
                lot_id=single_klarf.lot_id,
                device_id=single_klarf.device_id,
                step_id=single_klarf.step_id,
                wafer_id=single_klarf.wafer.id,
                inspection_tool=single_klarf.inspection_station_id.id,
                clusters=clusters,
                clustered_defects=clustered_defects,
                number_of_defects=nbr_defects,
                performance=ClusteringPerformance(
                    clustering_timestamp=round(clustering_timestamp, 3)
                ),
            )

            logger.info(
                f"Clustering complete. Found {clusters} cluster(s) on {nbr_defects} defect(s)."
            )

            output_timestamp = None
            if klarf_format == KlarfFormat.BABY.value and output_directory is not None:
                output_filename = (
                    output_directory
                    / f"{single_klarf.lot_id}_{single_klarf.step_id}_{single_klarf.wafer.id}_{clustering_mode}.000"
                )

                output_timestamp = klarf_lib.write_baby_klarf(
                    single_klarf=single_klarf,
                    clustering_result=clustering_result,
                    attribute=self.config.attribute,
                    output_filename=output_filename,
                )

                clustering_result.output_filename = output_filename
                clustering_result.performance.output_timestamp = round(
                    output_timestamp, 3
                )

            results.append(clustering_result)

        if klarf_format == KlarfFormat.FULL.value and output_directory is not None:
            if original_klarf_name is None:
                raise ValueError(
                    f"<original_klarf_name> cannot be None to create full klarf."
                )
            if original_klarf_extension is None:
                raise ValueError(
                    f"<original_klarf_extension> cannot be None to create full klarf."
                )

            output_filename = (
                output_directory
                / f"{original_klarf_name}_{clustering_mode}{original_klarf_extension}"
            )

            output_timestamp = klarf_lib.write_full_klarf(
                raw_klarf=raw_content,
                clustering_results=results,
                attribute=self.config.attribute,
                output_filename=output_filename,
            )

            for clustering_result in results:
                clustering_result.output_filename = output_filename
                clustering_result.performance.output_timestamp = round(
                    output_timestamp, 3
                )

        for clustering_result in results:
            defects = clustering_result.number_of_defects
            clusters = clustering_result.clusters

            logger.info(
                msg=f"({repr(clustering_result)}) was successfully processed [{defects=}, {clusters=}] with ({repr(clustering_result.performance)}) "
            )

        return results

    def apply_from_klarf_path(
        self,
        logger: Logger,
        klarf_path: Path,
        output_directory: str = None,
        klarf_format=KlarfFormat.BABY.value,
        clustering_mode=ClusteringMode.DBSCAN.value,
    ) -> List[ClusteringResult]:

        content = Klarf.load_from_file_with_raw_content(
            filepath=klarf_path,
            parse_summary=False,
            defects_as_generator=True,
        )

        return self.apply_from_content(
            logger=logger,
            content=content,
            output_directory=output_directory,
            original_klarf_name=klarf_path.stem,
            original_klarf_extension=klarf_path.suffix,
            klarf_format=klarf_format,
            clustering_mode=clustering_mode,
        )
