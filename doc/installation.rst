.. highlight:: shell

============
Installation
============


Stable release
--------------
xdatasets requires `conda` dependencies, you must make sure that they are all properly installed.
The best way to install them is by using `conda`.

First, install miniconda. Then, we recommend creating a new, clean environment:

.. code-block:: console

    $ conda create -n xdatasets_env
    $ conda activate xdatasets_env

Getting xdatasets is then as simple as:
.. code-block:: console

    $ conda install -c conda-forge xdatasets


Alternatively, you can first install conda dependencies, and then use pip to install xdatasets:

.. code-block:: console
    $ conda install -c conda-forge xarray s3fs zarr cartopy geoviews intake intake-xarray=0.6.1 xesfm
    $ pip install xdatasets


From sources
------------

The sources for Xdatasets can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/xdatasets/xdatasets

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/xdatasets/xdatasets/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/xdatasets/xdatasets
.. _tarball: https://github.com/xdatasets/xdatasets/tarball/master
