=========
Changelog
=========

0.3.0 (unreleased)
-------------------

* `xdatasets` now adheres to PEPs 517/518/621 using the `flit` backend for building and packaging.
* The `cookiecutter` template has been updated to the latest commit via `cruft`. (:pull:`28`):
    * `Manifest.in` and `setup.py` have been removed.
    * `pyproject.toml` has been added, with most package configurations migrated into it.
    * `HISTORY.rst` has been renamed to `CHANGES.rst`.
    * `actions-version-updater.yml` has been added to automate the versioning of the package.
    * `bump-version.yml` has been added to automate patch versioning of the package.
    * `pre-commit` hooks have been updated to the latest versions; `check-toml` and `toml-sort` have been added to cleanup the `pyproject.toml` file.
    * `ruff` has been added to the linting tools to replace most `flake8` and `pydocstyle` verifications.

0.1.2-alpha (2023-01-13)
---------------------------
First release on PyPI.
