# MODULES
import time
from pathlib import Path
from typing import List, Tuple
from logging import Logger

# NUMPY
import numpy as np

# SCIKIT_LEARN
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# HDBSCAN
from hdbscan import HDBSCAN

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
        logger: Logger = None,
    ) -> None:
        self.config = config
        self.logger = logger

    def apply_from_content(
        self,
        content: Tuple[KlarfContent, List[str]],
        output_directory: Path = None,
        original_klarf_name: str = None,
        original_klarf_extension: str = None,
        klarf_format=KlarfFormat.BABY.value,
        clustering_mode=ClusteringMode.DBSCAN.value,
    ):
        klarf_content, raw_content = content

        self.logger.info(f"Prepare to cluster {len(klarf_content.wafers)} wafer(s)")

        results: List[ClusteringResult] = []
        for index, wafer in enumerate(klarf_content.wafers):
            tic = time.time()

            single_klarf = klarf_convert.convert_to_single_klarf_content(
                klarf_content=klarf_content, wafer_index=index
            )

            lot = single_klarf.lot_id
            wafer_id = single_klarf.wafer.id
            nbr_defects = len(single_klarf.wafer.defects)

            match clustering_mode:
                case ClusteringMode.DBSCAN.value:
                    clustering = DBSCAN(
                        eps=self.config.clustering.dbscan.eps
                        if nbr_defects <= 30000
                        else 0.5,
                        min_samples=self.config.clustering.dbscan.min_samples,
                        # algorithm="ball_tree",
                        # metric="haversine",
                    )
                case ClusteringMode.HDBSCAN.value:
                    clustering = HDBSCAN(
                        min_samples=self.config.clustering.hdbscan.min_samples,
                        min_cluster_size=self.config.clustering.hdbscan.min_cluster_size,
                    )
                case _:
                    raise ValueError(f"{clustering_mode=} is not supported")

            self.logger.info(
                f"Preparing to perform clustering for {lot=} and {wafer_id=} using {clustering_mode=}"
            )

            if len(wafer.defects) == 0:
                clusters = 0
                clustered_defects = []
                clustering_timestamp = 0

                self.logger.info(f"{lot=} and {wafer_id=} do not have any defect")
            else:
                defect_ids = np.array([defect.id for defect in wafer.defects])
                defect_points = np.array(
                    [
                        (defect.point[0] / 1000, defect.point[1] / 1000)
                        for defect in wafer.defects
                    ]
                )

                self.logger.info(
                    f"Starting clustering process for {lot=} and {wafer_id=} on {nbr_defects} defect(s)"
                )

                labels = clustering.fit_predict(defect_points)

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
                clusters=clusters,
                clustered_defects=clustered_defects,
                performance=ClusteringPerformance(
                    clustering_timestamp=round(clustering_timestamp, 3)
                ),
            )

            self.logger.info(
                f"Clustering complete. Found {clusters} clusters on {len(clustered_defects)} defects."
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

        if self.logger is not None:
            for clustering_result in results:
                defects = len(clustering_result.clustered_defects)
                clusters = clustering_result.clusters

                self.logger.info(
                    msg=f"({repr(clustering_result)}) was sucessfully processed [{defects=}, {clusters=}] with ({repr(clustering_result.performance)}) "
                )

        return results

    def apply_from_klarf_path(
        self,
        klarf_path: Path,
        output_directory: str = None,
        klarf_format=KlarfFormat.BABY.value,
        clustering_mode=ClusteringMode.DBSCAN.value,
    ) -> List[ClusteringResult]:

        content = Klarf.load_from_file_with_raw_content(
            filepath=klarf_path,
            parse_summary=False,
        )

        return self.apply_from_content(
            content=content,
            output_directory=output_directory,
            original_klarf_name=klarf_path.stem,
            original_klarf_extension=klarf_path.suffix,
            klarf_format=klarf_format,
            clustering_mode=clustering_mode,
        )
