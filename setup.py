from setuptools import setup

version = "0.2.5"

setup(
    name="wafermap-clustering",
    version=version,
    packages=[
        "wafermap_clustering",
        "wafermap_clustering.configs",
        "wafermap_clustering.libs",
        "wafermap_clustering.models",
    ],
    install_requires=[
        "klarf-reader",
        "scikit-learn",
    ],
    license="MIT",
    author="Maxime MARTIN",
    author_email="maxime.martin02@hotmail.fr",
    description="A project to apply clustering on wafermaps",
    url="https://github.com/Impro02/wafermap-clustering",
    download_url="https://github.com/Impro02/wafermap-clustering/archive/refs/tags/%s.tar.gz"
    % version,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
