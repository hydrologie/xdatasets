=========
Changelog
=========

v0.3.5 (2024-02-19)
-------------------

* The `cookiecutter` template has been updated to the latest commit via `cruft`. (:pull:`52`):
    * `xdatasets` is now `Semantic Version v2.0.0 <https://semver.org/spec/v2.0.0.html>`_-compliant
    * Added a few workflows (Changed file labelling, Cache cleaning, Dependency Scanning, OpenSSF Scorecard)
    * Workflows now use the `tep-security/harden-runner` action to security harden the runner environment
    * Reorganized README and added a few badges
    * Updated pre-commit hook versions
    * Formatting tools (`black`, `blackdoc`, `isort`) are now pinned to their pre-commit version equivalents
    * `actions-version-updater.yml` has been replaced by `dependabot`
* Enabled the `labeler.yml` workflow to mark changed files in Pull Requests as "CI". (:pull:`63`).
* Enabled the Anaconda build tests and coverage reporting to `Coveralls.io <https://coveralls.io>`_. (:pull:`63`).
* Removed the version pin on `ipython`. (:pull:`63`).
* Migrated the documentation from GitHub Pages to ReadTheDocs. (:issue:`32`, :pull:`67`).

v0.3.4 (2024-01-31)
-------------------

* Fix user-defined climate request (:pull:`50`)

v0.3.3 (2024-01-11)
-------------------

* Support hydrometric queries when dataset's coordinates are lazy. (:pull:`46`)

v0.3.2 (2024-01-10)
-------------------

* Update documentation. (:pull:`42`)
* Added a functionality to extract geometries to a `geopandas.GeoDataFrame` format. (:pull:`42`)

v0.3.1 (2023-12-01)
-------------------

* Patch update to address a missing dependency (`s3fs`). (:pull:`36`)

v0.3.0 (2023-11-30)
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

v0.1.2-alpha (2023-01-13)
-------------------------
First release on PyPI.
