#!/usr/bin/env python
"""The setup script."""
import re

from setuptools import find_packages, setup

NAME = "xdatasets"
DESCRIPTION = "Easy acess to earth observation datasets with xarray."
URL = "https://github.com/hydrologie/xdatasets'"
AUTHOR = "Sebastien Langlois"
AUTHOR_EMAIL = "sebastien.langlois62@gmail.com"
REQUIRES_PYTHON = ">=3.8.0"
LICENSE = "MIT license"

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "bottleneck>=1.3.1",
    "cf-xarray>=0.6.1",
    "cftime>=1.4.1",
    "clisops>=0.9.2",
    "dask[array]>=2.6",
    "intake-xarray>=0.6.1",
    "jsonpickle",
    "numba",
    "numpy>=1.16",
    "pandas>=0.23",
    "pint>=0.10",
    "pyyaml",
    "s3fs>=2022.7.0",
    "geopandas",
    "tqdm",
    "scipy>=1.2",
    "xarray>=0.17",
    "zarr>=2.11.1",
    "xagg-no-xesmf-deps"
]


dev_requirements = []
with open("requirements_dev.txt") as dev:
    for dependency in dev.readlines():
        dev_requirements.append(dependency)

KEYWORDS = "xdatasets hydrology meteorology climate climatology netcdf gridded analysis"

setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
    description=DESCRIPTION,
    python_requires=REQUIRES_PYTHON,
    install_requires=requirements,
    license=LICENSE,
    long_description="Xdatasets",
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords=KEYWORDS,
    name=NAME,
    packages=find_packages(),
    extras_require={"dev": dev_requirements},
    url=URL,
    version='0.2.1',
    zip_safe=False,
)
