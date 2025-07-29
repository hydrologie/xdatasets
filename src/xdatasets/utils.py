import os
import sys
import tempfile
import getpass
import urllib.request
import warnings
from functools import reduce
from pathlib import Path

import intake

catalog_path = "https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/main.yaml"


def open_dataset(
    name: str,
    catalog,
    **kws,  # noqa: F841
):
    r"""
    Open a dataset from the online public repository (requires internet).

    Parameters
    ----------
    name : str
        Name of the file containing the dataset.
        e.g. 'era5_reanalysis_single_levels'.
    catalog : str
        URL for the intake catalog which provides access to the datasets.
    \*\*kws : dict, optional
        Currently not used.

    See Also
    --------
    xarray.open_dataset

    Notes
    -----
    Available datasets:
        `"era5_reanalysis_single_levels"`: ERA5 reanalysis subset (t2m and tp).
        `"cehq"`: CEHQ flow and water levels observations.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        try:
            import intake  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "tutorial.open_dataset depends on intake and intake-xarray to download and manage datasets."
                " To proceed please install intake and intake-xarray.",
            ) from e

        cat = catalog
        dataset_info = [
            (category, dataset_name)
            for category in cat._entries.keys()
            for dataset_name in cat[category]._entries.keys()
            if dataset_name == name
        ]

        data = reduce(lambda array, index: array[index], dataset_info, cat)

        # add proxy infos
        proxies = urllib.request.getproxies()
        storage_options = data.storage_options
        storage_options["config_kwargs"]["proxies"] = proxies

        if data.describe()["driver"][0] == "geopandasfile":
            data = data(storage_options=storage_options).read()
        elif data.describe()["driver"][0] == "zarr":
            data = data(storage_options=storage_options).to_dask()
        else:
            raise NotImplementedError(
                f"Dataset {name} is not available. Please request further datasets to our github issues pages",
            )
    return data


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = Path(os.devnull).open("w")

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: F841
        sys.stdout.close()
        sys.stdout = self._original_stdout


def cache_catalog(url):
    """
    Cache the catalog in the system's temporary folder for easier access.

    This is especially useful when working behind firewalls or if the remote server containing the yaml files is down.
    Looks for http_proxy/https_proxy environment variable if the request goes through a proxy.

    Parameters
    ----------
    url : str
        URL for the intake catalog which provides access to the datasets.
        While this library provides its own intake catalog, users have the option to provide their own catalog,
        which can be particularly beneficial for private datasets or if different configurations are needed.
    """
    proxies = urllib.request.getproxies()
    proxy = urllib.request.ProxyHandler(proxies)
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)

    tmp_dir = (
        Path(tempfile.gettempdir()).joinpath(getpass.getuser()).joinpath("catalogs")
    )
    tmp_dir.mkdir(parents=True, exist_ok=True)
    main_catalog_path = tmp_dir.joinpath(Path(url).name)

    try:
        urllib.request.urlretrieve(url, main_catalog_path)  # noqa: S310
    except urllib.error.URLError as e:
        raise urllib.error.URLError(
            "Could not reach the catalog, perhaps due to the presence of a proxy."
            "Try adding proxy information to the environment variables as follows before"
            "running xdatasets :"
            "import os"
            "proxy = 'http://<proxy>:<port>'"
            "os.environ['http_proxy'] = proxy"
            "os.environ['https_proxy'] = proxy",
        ) from e

    for value in intake.open_catalog(main_catalog_path)._entries.values():
        # FIXME: entry_path only seems to work using os.path, and not pathlib.Path. Why is that?
        entry_path = f"{os.path.dirname(url)}/{Path(value.describe()['args']['path']).name}"  # noqa: PTH120
        urllib.request.urlretrieve(  # noqa: S310
            entry_path,
            tmp_dir.joinpath(Path(entry_path).name),
        )
    return main_catalog_path
