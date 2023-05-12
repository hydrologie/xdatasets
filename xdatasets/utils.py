import datetime
import time
from functools import reduce
import os, sys
import urllib
from pathlib import Path
import tempfile
import intake

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

    # add proxy infos
    proxies=urllib.request.getproxies()
    storage_options = data.storage_options
    storage_options['config_kwargs']['proxies'] = proxies

    if data.describe()['driver'][0] == 'geopandasfile':
        data =  data(storage_options=storage_options).read()
    elif data.describe()['driver'][0] == 'zarr':
        data = data(storage_options=storage_options).to_dask()
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


def cache_catalog(url):

    proxies=urllib.request.getproxies()
    #create the object, assign it to a variable
    proxy = urllib.request.ProxyHandler(proxies)
    # construct a new opener using your proxy settings
    opener = urllib.request.build_opener(proxy)
    # install the openen on the module-level
    urllib.request.install_opener(opener)
    #response = urllib.request.urlopen(req)
 
    tmp_dir = os.path.join(tempfile.gettempdir(), 'catalogs')
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)
    main_catalog_path = os.path.join(tmp_dir,os.path.basename(url))
    urllib.request.urlretrieve(url, main_catalog_path)

    for key, value in intake.open_catalog(os.path.join(tmp_dir,os.path.basename(url)))._entries.items():
        path = f"{os.path.dirname(url)}/{os.path.basename(value.describe()['args']['path'])}"
        urllib.request.urlretrieve(path, os.path.join(tmp_dir,os.path.basename(path)))

    return main_catalog_path

 

