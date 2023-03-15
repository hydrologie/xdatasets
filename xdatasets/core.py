from typing import Sequence, Tuple, Union, Dict, List, Optional
import warnings
import logging

import intake
import geopandas as gpd
import xarray as xr
import hvplot.xarray
import hvplot.pandas

from .spatial import clip_by_polygon, clip_by_point
from .temporal import change_timezone, temporal_aggregation
from .validations import _validate_space_params
from .utils import open_dataset
from .workflows import climate_request


URL_PATH = 'https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/main.yaml'

__all__ = ["Query"]

logger = logging.getLogger()
logger.handlers = []

# Start defining and assigning your handlers here
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class Query:

    """"The Query interface facilitates access to analysis-ready 
    earth observation datasets and allows for spatiotemporal
    operations to be performed based on user queries.
        
    Parameters
    ----------
    datasets : str, list, dict-like
        A dictionary that maps dataset names to their corresponding requested 
        content such as some desired variables. If a string representing only the dataset 
        name is provided, then the object will return all content within that dataset.
        If a list is provided, then the object will return all content from each dataset
        from that list.

        The following notations are accepted:
        - str (first_dataset_name)
        - list [first_dataset_name, second_dataset_name]
        - mapping {first_dataset_name: {key: value, key2: value2},
                   second_dataset_name: {key: value}
                   }
          Currently, accepted key, value pairs for a mapping argument include the following:
            - Optional: {"variables": [var1_name, var2_name]}
        
        The list of datasets available in this library can be accessed here:
        # Coming soon!

    space : dict-like
        A dictionary that maps spatial parameters with their corresponding value.
        More information on accepted key/value pairs : :py:meth:`~xdatasets.Query._resolve_space_params` 


    time : dict-like
        A dictionary that maps temporal parameters with their corresponding value.
        Currently, accepted key, value pairs include the following:
            - Optional: {"timestep": timestep (str)} -> timestep refers to the time interval of the data that is retrieved by the query. 
                        Offset aliases can be any of: 
                        http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases 

            - Optional: {"aggregation": {var1_name (str): operation1 (str, List[str]),
                                         var2_name (str): operation2 (str, List[str])}} -> For each variable var1_name, 
                        var2_name, etc., which numpy operation(s) (str or list of str) to use for temporal aggregation

            - Optional: {"start": start (str)} -> Start date of the subset. 
                        Date string format – can be year (“%Y”), year-month (“%Y-%m”) or year-month-day(“%Y-%m-%d”)     

            - Optional: {"end": end (str)} -> End date of the subset. 
                        Date string format – can be year (“%Y”), year-month (“%Y-%m”) or year-month-day(“%Y-%m-%d”)
                        
            - Optional: {"timezone": timezone (str)} -> Which timezone should the query return the data in. Possible values are listed here:
                        https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568


    catalog_path: str
        URL for the intake catalog which provides access to the datasets. While
        this library provides its own intake catalog, users have the option to 
        provide their own catalog, which can be particularly beneficial for 
        private datasets or if different configurations are needed.

    Examples
    --------
    Create data:

    >>> sites = {
    ...    'Montreal' : (45.508888, -73.561668),
    ...    'New York': (40.730610, -73.935242),
    ...    'Miami': (25.761681, -80.191788)
    ... }

    >>> query = {
    ...     "datasets": 'era5_land_reanalysis_dev',
    ...     "space": {
    ...         "clip": "point",
    ...         "geometry": sites
    ...     },
    ...     "time": {        
    ...         "timestep": "D",
    ...         "aggregation": {"tp": np.nansum,
    ...                         "t2m": np.nanmean},
    ...         "start": '1950-01-01',
    ...         "end": '1955-12-31',
    ...         "timezone": 'America/Montreal',
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

    def __init__(self,
                 datasets: Union[str, List[str], Dict[str, Union[str, List[str]]]],
                 space: Dict[str, Union[str, List[str]]],
                 time=dict(),
                 catalog_path: str = URL_PATH):
        
        # assert datasets params
        # assert time params

        self.catalog = intake.open_catalog(catalog_path)
        self.datasets = datasets
        self.space = self._resolve_space_params(**space)
        self.time = time
        
        self.load_query(datasets=self.datasets,
                        space=self.space,
                        time=self.time)
        

    def _resolve_space_params(self,
                              clip: str, 
                              geometry: Union[Dict[str, tuple], gpd.GeoDataFrame],
                              averaging: Optional[bool] = False,
                              unique_id: Optional[str] = None):
        
        
        """ 
        Resolves and validates user-provided space params before

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
        space.pop('self')

        assert _validate_space_params(**space)
        
        if isinstance(geometry, gpd.GeoDataFrame ):
            geometry = geometry.reset_index(drop=True)

        # We created a new dict based on user-provided parameters
        # TODO : adapt all parameters before requesting any operations on datasets
        args = {'clip': clip,
                'geometry': geometry,
                'averaging': averaging,
                'unique_id': unique_id}

        return args


    
    def load_query(self,
                   datasets: Union[str, Dict[str, Union[str, List[str]]]],
                   space: Dict[str, Union[str, List[str]]],
                   time):
        
        # Get all datasets in query
        if isinstance(datasets, str):
            datasets_name = [datasets]

        elif isinstance(datasets, dict):
            datasets_name = list(datasets.keys())

        # Load data for each dataset
        dsets = []
        for dataset_name in datasets_name:
            try:
                variables_name = self.datasets[dataset_name]['variables']
            except:
                variables_name = None
                pass

            ds_one = self._process_one_dataset(dataset_name=dataset_name,
                                               variables=variables_name,
                                               space=space,
                                               time=time)
            dsets.append(ds_one)
            
        try:
            # Try naively merging datasets into single dataset
            ds = xr.merge(dsets)
            ds = ds
        except:
            logging.warn("Couldn't merge datasets so we pass a dictionary of datasets. ")
            # Look into passing a DataTree instead
            ds = dsets
            pass

        self.data = ds

        return self

    def _process_one_dataset(self,
                             dataset_name,
                             variables,
                             space,
                             time):
        
        dataset_category = [category for category in self.catalog._entries.keys()
                                     for name in self.catalog[category]._entries.keys() 
                                     if name == dataset_name][0]
        
        if dataset_category in ['atmosphere']:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                ds = climate_request(dataset_name,
                                    variables,
                                    space,
                                    time,
                                    self.catalog)
        
        return ds
    
    def bbox_clip(self, ds):
        return ds.where(~ds.isnull(), drop=True)

    def plot(self,
             variables=None):

        variables = ['t2m', 'tp']

        return self.data[variables].hvplot(x='time', grid=True, subplots=True, shared_axes=False, by='geom', legend=True).cols(1)
    




