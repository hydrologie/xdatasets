#!/usr/bin/env python
"""Tests for `xdatasets` package."""

import pathlib
from importlib.util import find_spec

import xdatasets  # noqa: F401

# import pytest


# @pytest.fixture
# def response():
#     """Sample pytest fixture.
#
#     See more at: https://doc.pytest.org/en/latest/explanation/fixtures.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_package_metadata():
    """Test the package metadata."""
    project = find_spec("xdatasets")

    assert project is not None
    assert project.submodule_search_locations is not None
    location = project.submodule_search_locations[0]

    metadata = pathlib.Path(location).resolve().joinpath("__init__.py")

    with metadata.open() as f:
        contents = f.read()
        assert """Sebastien Langlois""" in contents
        assert '__email__ = "sebastien.langlois62@gmail.com"' in contents
        assert '__version__ = "0.3.9-dev.0"' in contents
