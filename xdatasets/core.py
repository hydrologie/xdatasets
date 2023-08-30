import logging
import warnings
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import geopandas as gpd
import hvplot.pandas
import hvplot.xarray
import intake
import xarray as xr

from .scripting import LOGGING_CONFIG
from .utils import cache_catalog
from .validations import _validate_space_params
from .workflows import climate_request, hydrometric_request, user_provided_dataset

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

url_path = "https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/main.yaml"


__all__ = ["Query"]


class Query:

    """ "The Query interface facilitates access to analysis-ready
    earth observation datasets and allows for spatiotemporal
    operations to be performed based on user queries.

    Parameters
    ----------
    datasets : str, list, dict-like
        - If str, a dataset name, i.e.: era5_land_reanalysis
        - If list, a list of dataset names, i.e.: [era5_single_levels_reanalysis, era5_land_reanalysis]
        - If dictionary, it should map dataset names to their corresponding requested
          content such as some desired variables. This allows more flexibility in the request.
              i.e.: {era5_land_reanalysis: {'variables': ['t2m', 'tp]},
                    era5_single_levels_reanalysis: {'variables': 't2m'}
                     }
              Currently, accepted key, value pairs for a mapping argument include the following:
              ===========  ==============
              Key          Variables
              ===========  ==============
              variables    str, List[str]
              ===========  ==============

        The list of available datasets in this library can be accessed here:
        # Coming soon!
    space : dict-like
        A dictionary that maps spatial parameters with their corresponding value.
        More information on accepted key/value pairs : :py:meth:`~xdatasets.Query._resolve_space_params`
    time : dict-like
        A dictionary that maps temporal parameters with their corresponding value.
        More information on accepted key/value pairs : :py:meth:`~xdatasets.Query._resolve_time_params`
    catalog_path: str
        URL for the intake catalog which provides access to the datasets. While
        this library provides its own intake catalog, users have the option to
        provide their own catalog, which can be particularly beneficial for
        private datasets or if different configurations are needed.

    Examples
    --------
    Create data:

    >>> sites = {
    ...     "Montreal": (45.508888, -73.561668),
    ...     "New York": (40.730610, -73.935242),
    ...     "Miami": (25.761681, -80.191788),
    ... }

    >>> query = {
    ...     "datasets": "era5_land_reanalysis_dev",
    ...     "space": {"clip": "point", "geometry": sites},
    ...     "time": {
    ...         "timestep": "D",
    ...         "aggregation": {"tp": np.nansum, "t2m": np.nanmean},
    ...         "start": "1950-01-01",
    ...         "end": "1955-12-31",
    ...         "timezone": "America/Montreal",
    ...     },
    ... }
    >>> xds = xd.Query(**query)
    >>> xds.data
    <xarray.Dataset>
    Dimensions:      (site: 3, time: 2191, source: 1)
    Coordinates:
        latitude     (site) float64 45.5 40.7 25.8
        longitude    (site) float64 -73.6 -73.9 -80.2
      * site         (site) <U8 'Montreal' 'New York' 'Miami'
      * time         (time) datetime64[ns] 1950-01-01 1950-01-02 ... 1955-12-31
      * source       (source) <U24 'era5_land_reanalysis_dev'
    Data variables:
        t2m_nanmean  (time, site, source) float32 269.6 273.8 294.3 ... 268.1 292.1
        tp_nansum    (time, site, source) float32 0.0004192 2.792e-06 ... 0.0001207
    Attributes:
        pangeo-forge:inputs_hash:  1622c0abe9326bfa4d6ee6cdf817fccb1ef1661046f30f...
        pangeo-forge:recipe_hash:  f2b6c75f28693bbae820161d5b71ebdb9d740dcdde0666...
        pangeo-forge:version:      0.9.4

    """

    def __init__(
        self,
        datasets: Union[str, List[str], Dict[str, Union[str, List[str]]]],
        space: Dict[str, Union[str, List[str]]] = dict(),
        time: Dict[str, Union[str, List[str]]] = dict(),
        catalog_path: str = url_path,
    ) -> None:
        # We cache the catalog's yaml files for easier access behind corporate firewalls
        catalog_path = cache_catalog(catalog_path)

        self.catalog = intake.open_catalog(catalog_path)
        self.datasets = datasets
        self.space = self._resolve_space_params(**space)
        self.time = self._resolve_time_params(**time)

        self.load_query(datasets=self.datasets, space=self.space, time=self.time)

    def _resolve_space_params(
        self,
        clip: str = None,
        geometry: Union[Dict[str, tuple], gpd.GeoDataFrame] = None,
        averaging: Optional[bool] = False,
        unique_id: Optional[str] = None,
    ) -> Dict:
        """
        Resolves and validates user-provided space params

        Parameters
        ----------
        clip : str
            Which kind of clip operation to perform on geometry.
            Possible values are one of "polygon", "point" or "bbox".
        geometry : gdf.DataFrame, Dict[str, Tuple]
            Geometry/geometries on which to perform spatial operations
        averaging : bool, optional
            Whether to spatially average the arrays within a geometry or not
        unique_id : str, optional
            a column name, if gdf.DataFrame is provided, to identify each unique geometry
        """

        space = locals()
        space.pop("self")

        assert _validate_space_params(**space)

        if isinstance(geometry, gpd.GeoDataFrame):
            geometry = geometry.reset_index(drop=True)

        # We created a new dict based on user-provided parameters
        # TODO : adapt all parameters before requesting any operations on datasets
        args = {
            "clip": clip,
            "geometry": geometry,
            "averaging": averaging,
            "unique_id": unique_id,
        }

        return args

    def _resolve_time_params(
        self,
        timestep: Optional[str] = None,
        aggregation: Optional[
            Dict[str, Union[Callable[..., Any], List[Callable[..., Any]]]]
        ] = None,
        start: Optional[bool] = None,
        end: Optional[str] = None,
        timezone: Optional[str] = None,
        minimum_duration: Optional[str] = None,
    ) -> Dict:
        """
        Resolves and validates user-provided time params

        Parameters
        ----------
        timestep : str, optional
            In which time step should the data be returned
            Possible values : http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        aggregation : Dict[str, callable], optional
            Mapping that associates a variable name with the aggregation function
            to be applied to it. Function which can be called in the form
            `f(x, axis=axis, **kwargs)` to return the result of reducing an
            np.ndarray over an integer valued axis. This parameter is required
            should the `timestep` argument be passed.
        start : str, optional
            Start date of the selected time period.
            String format – can be year (“%Y”), year-month (“%Y-%m”) or
            year-month-day(“%Y-%m-%d”)
        end : str, optional
            End date of the selected time period.
            String format – can be year (“%Y”), year-month (“%Y-%m”) or
            year-month-day(“%Y-%m-%d”)
        timezone : str, optional
            Timezone to be used for the returned datasets
            Possible values are listed here:
            https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
        minimum_duration : str, optional
            Minimum duration of a time series (id) in order to be kept
            Possible values : http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        """

        space = locals()
        space.pop("self")

        # assert _validate_time_params(**space)

        # We created a new dict based on user-provided parameters
        # TODO : adapt all parameters before requesting any operations on datasets
        args = {
            "timestep": timestep,
            "aggregation": aggregation,
            "start": start,
            "end": end,
            "timezone": timezone,
            "minimum_duration": minimum_duration,
        }

        return args

    def load_query(
        self,
        datasets: Union[str, Dict[str, Union[str, List[str]]]],
        space: Dict[str, Union[str, List[str]]],
        time,
    ):
        # Get all datasets in query
        if isinstance(datasets, str):
            datasets_name = [datasets]

        elif isinstance(datasets, dict):
            datasets_name = list(datasets.keys())

        # Load data for each dataset
        dsets = []
        for dataset_name in datasets_name:
            data = None
            kwargs = {}
            try:
                variables_name = self.datasets[dataset_name]["variables"]
                if isinstance(variables_name, str):
                    variables_name = [variables_name]
            except:
                variables_name = None
                pass
            try:
                kwargs = {
                    k: v
                    for k, v in self.datasets[dataset_name].items()
                    if k not in ["variables"]
                }
            except:
                pass

            ds_one = self._process_one_dataset(
                dataset_name=dataset_name,
                variables=variables_name,
                space=space,
                time=time,
                **kwargs,
            )
            dsets.append(ds_one)

        try:
            # Try naively merging datasets into single dataset
            ds = xr.merge(dsets)
            ds = ds
        except:
            logging.warn(
                "Couldn't merge datasets so we pass a dictionary of datasets. "
            )
            # Look into passing a DataTree instead
            ds = dsets
            pass

        self.data = ds

        return self

    def _process_one_dataset(self, dataset_name, variables, space, time, **kwargs):
        data = None
        if "data" in kwargs:
            data = kwargs["data"]

        if data != None and isinstance(data, xr.Dataset):
            dataset_category = "user-provided"

        elif isinstance(dataset_name, str):
            dataset_category = [
                category
                for category in self.catalog._entries.keys()
                for name in self.catalog[category]._entries.keys()
                if name == dataset_name
            ][0]

        if dataset_category in ["atmosphere"]:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                ds = climate_request(dataset_name, variables, space, time, self.catalog)

        elif dataset_category in ["hydrology"]:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                ds = hydrometric_request(
                    dataset_name, variables, space, time, self.catalog, **kwargs
                )

        elif dataset_category in ["user-provided"]:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                ds = user_provided_dataset(dataset_name, variables, space, time, data)

        return ds

    def bbox_clip(self, ds):
        """ """
        return ds.where(~ds.isnull(), drop=True)
