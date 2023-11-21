.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/hydrologie/xdatasets/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

xdatasets could always use more documentation, whether as part of the
official xdatasets docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/hydrologie/xdatasets/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `xdatasets` for local development.

#. Fork the `xdatasets` repo on GitHub.
#. Clone your fork locally::

    $ git clone git@github.com:your_name_here/xdatasets.git

#. Install your local copy into a development environment. Using `mamba`, you can create a new development environment with::

    $ mamba env create -f environment-dev.yml
    $ conda activate xdatasets
    $ flit install --symlink .

#. To ensure a consistent style, please install the pre-commit hooks to your repo::

    $ pre-commit install

   Special style and formatting checks will be run when you commit your changes. You
   can always run the hooks on their own with:

    $ pre-commit run -a

#. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

#. When you're done making changes, check that your changes pass black, flake8, isort, and the
   tests, including testing other Python versions with tox::

    $ black --check xdatasets tests
    $ flake8 xdatasets tests
    $ isort --check-only --diff xdatasets tests
    $ python -m pytest
    $ tox

   To get flake8, black, and tox, just pip install them into your virtualenv.

#. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

#. If you are editing the docs, compile and open them with::

    $ make docs
    # or to simply generate the html
    $ cd docs/
    $ make html

#. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.8, 3.9, 3.10, and 3.11. Check that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::

$ pytest tests.test_xdatasets

Versioning/Tagging
------------------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bumpversion patch # possible: major / minor / patch
$ git push
$ git push --tags

Packaging
---------

When a new version has been minted (features have been successfully integrated test coverage and stability is adequate),
maintainers should update the pip-installable package (wheel and source release) on PyPI as well as the binary on conda-forge.

The simple approach
~~~~~~~~~~~~~~~~~~~

The simplest approach to packaging for general support (pip wheels) requires the following packages installed:
 * build
 * setuptools
 * twine
 * wheel

From the command line on your Linux distribution, simply run the following from the clone's main dev branch::

    # To build the packages (sources and wheel)
    $ python -m build --sdist --wheel

    # To upload to PyPI
    $ twine upload dist/*

The new version based off of the version checked out will now be available via `pip` (`$ pip install xdatasets`).

Releasing on conda-forge
~~~~~~~~~~~~~~~~~~~~~~~~

Initial Release
^^^^^^^^^^^^^^^

In order to prepare an initial release on conda-forge, we *strongly* suggest consulting the following links:
 * https://conda-forge.org/docs/maintainer/adding_pkgs.html
 * https://github.com/conda-forge/staged-recipes

Before updating the main conda-forge recipe, we echo the conda-forge documentation and *strongly* suggest performing the following checks:
 * Ensure that dependencies and dependency versions correspond with those of the tagged version, with open or pinned versions for the `host` requirements.
 * If possible, configure tests within the conda-forge build CI (e.g. `imports: xdatasets`, `commands: pytest xdatasets`)

Subsequent releases
^^^^^^^^^^^^^^^^^^^

If the conda-forge feedstock recipe is built from PyPI, then when a new release is published on PyPI, `regro-cf-autotick-bot` will open Pull Requests automatically on the conda-forge feedstock. It is up to the conda-forge feedstock maintainers to verify that the package is building properly before merging the Pull Request to the main branch.

Building sources for wide support with `manylinux` image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
    This section is for building source files that link to or provide links to C/C++ dependencies.
    It is not necessary to perform the following when building pure Python packages.

In order to do ensure best compatibility across architectures, we suggest building wheels using the `PyPA`'s `manylinux`
docker images (at time of writing, we endorse using `manylinux_2_24_x86_64`).

With `docker` installed and running, begin by pulling the image::

    $ sudo docker pull quay.io/pypa/manylinux_2_24_x86_64

From the xdatasets source folder we can enter into the docker container, providing access to the `xdatasets` source files by linking them to the running image::

    $ sudo docker run --rm -ti -v $(pwd):/xdatasets -w /xdatasets quay.io/pypa/manylinux_2_24_x86_64 bash

Finally, to build the wheel, we run it against the provided Python3.8 binary::

    $ /opt/python/cp38-cp38m/bin/python -m build --sdist --wheel

This will then place two files in `xdatasets/dist/` ("xdatasets-1.2.3-py3-none-any.whl" and "xdatasets-1.2.3.tar.gz").
We can now leave our docker container (`$ exit`) and continue with uploading the files to PyPI::

    $ twine upload dist/*
