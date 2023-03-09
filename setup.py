from setuptools import setup

version = "0.1.0"

setup(
    name="wafermap-clustering",
    version=version,
    packages=[
        "wafermap_clustering",
        "wafermap_clustering.configs",
        "wafermap_clustering.libs",
        "wafermap_clustering.models",
        "wafermap_clustering.utils",
    ],
    install_requires=[
        "numpy",
        "klarf-reader",
        "scikit-learn",
    ],
    license="MIT",
    author="Maxime MARTIN",
    author_email="maxime.martin02@hotmail.fr",
    description="A project to apply clustering in wafermaps",
    url="https://github.com/Impro02/klarf_reader",
    download_url="https://github.com/Impro02/wafermap_clustering/archive/refs/tags/%s.tar.gz"
    % version,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
