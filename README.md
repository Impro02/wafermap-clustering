# Wafermap Clustering

This project applies clustering algorithms on wafermaps. It's designed to help you analyze and categorize wafermaps based on their patterns.

## Installation

Ensure you have Python installed on your system. You can then install `wafermap-clustering` using pip:

```bash
pip install wafermap-clustering
```

## Configuration

The project can be configured using a JSON file. Here's an example of the configuration file:


```
{
    "project_name": "wafermap-clustering",
    "directories": {
        "root": "/{{project_name}}",
        "logs": "{{home}}/logs",
        "tmp": "{{home}}/tmp"
    },
    "attribute": "CLUSTER_ID",
    "clustering": {
        "dbscan": {
            "epsilon_values": [
                {
                    "min_points": 0,
                    "max_points": 15000,
                    "epsilon": 4
                },
                {
                    "min_points": 15000,
                    "max_points": 35000,
                    "epsilon": 1
                },
                {
                    "min_points": 35000,
                    "max_points": 75000,
                    "epsilon": 0.1
                },
                {
                    "min_points": 75000,
                    "max_points": null,
                    "epsilon": 0.01
                }
            ],
            "min_samples": 3
        },
        "hdbscan": {
            "min_samples": 3,
            "min_cluster_size": 5,
            "epsilon_values": [
                {
                    "min_points": 0,
                    "max_points": 15000,
                    "epsilon": 4
                },
                {
                    "min_points": 15000,
                    "max_points": 35000,
                    "epsilon": 1
                },
                {
                    "min_points": 35000,
                    "max_points": 75000,
                    "epsilon": 0.1
                },
                {
                    "min_points": 75000,
                    "max_points": null,
                    "epsilon": 0.01
                }
            ]
        }
    }
}
```

## Usage

After installing and configuring the project, you can start using it to cluster your wafermaps.

```python
from logging import get_logger
from wafermap_clustering.configs.config import (
    ClusteringMode,
    Config,
    KlarfFormat,
)

config_path = "my_path.json"
klarf_path = "klarf.000"

config = Config(conf_path=config_path)

logger = get_logger("clustering")

clustering = Clustering(config=config)
results = clustering.apply_from_klarf_path(
    logger=logger,
    klarf_path=klarf_path,
    klarf_format=KlarfFormat.FULL.value,
    clustering_mode=ClusteringMode.DBSCAN.value,
)
```

## Contributing

Contributions are welcome. Please open an issue or submit a pull request if you would like to contribute to the project.

## License

This project is licensed under the MIT License. See the LICENSE.txt file for details.