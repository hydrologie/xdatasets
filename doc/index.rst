Welcome to Xdatasets's documentation!
======================================

Xdataset is a project whose objective is to facilitate access to Earth observation big data by centralizing access via a single catalog.

This project does not want to reinvent the wheel. We use technologies that are already well established in the field of earth observation to format and organize our datasets (intake, STAC, zarr, netcdf, etc.). When not required, we don't change anything in a dataset, we just point to the original provider's servers. What we do however is that we maintain one single catalog from multiple providers and for each dataset, we document the steps required to access it in multiple programming languages (focusing on Python for now, but eventually Julia and R). For some datasets, we also take extra steps such as rechunking the data, deaggregate or decumulate some variables, all to make life easier for users.

This project was born out of a fundamental need to share common data sources when we were doing research. We collaborate with researchers, engineers, data scientists from academia to industry. In multidisciplinary projects, we have experienced difficulties in sharing and working on large common datasets. Although the centralization of data brought by cloud computing has made this task easier for us, the fact remains that there is still a significant learning curve to interact with these datasets and that the documentation to achieve this via different programming languages is sometimes limited.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   installation
   notebooks/load_data
   modules
   contributing
   authors
   history

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
