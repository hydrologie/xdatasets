import datetime
import time
from functools import reduce
import os, sys

catalog_path = 'https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/main.yaml'

def open_dataset(
    name,
    catalog,
    **kws,
):
    """
    Open a dataset from the online public repository (requires internet).
    Available datasets:
    * ``"era5_reanalysis_single_levels"``: ERA5 reanalysis subset (t2m and tp)
    * ``"cehq"``: CEHQ flow and water levels observations 
    Parameters
    ----------
    name : str
        Name of the file containing the dataset.
        e.g. 'era5_reanalysis_single_levels'
    **kws : dict, optional
        Passed to xarray.open_dataset
    See Also
    --------
    xarray.open_dataset
    """
    try:
        import intake
    except ImportError as e:
        raise ImportError(
            "tutorial.open_dataset depends on intake and intake-xarray to download and manage datasets."
            " To proceed please install intake and intake-xarray."
        ) from e

    cat = catalog
    dataset_info = [(category, dataset_name)  for category in cat._entries.keys()
     for dataset_name in cat[category]._entries.keys() if dataset_name == name]
     
    data = reduce(lambda array, index : array[index], dataset_info, cat)

    if data.describe()['driver'][0] == 'geopandasfile':
        data =  data.read()
    elif data.describe()['driver'][0] == 'zarr':
        data = data.to_dask() 
    else:
        raise NotImplementedError(f'Dataset {name} is not available. Please request further datasets to our github issues pages')
    return data  


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout