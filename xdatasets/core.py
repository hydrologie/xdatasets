from typing import Sequence, Tuple, Union, Dict, List, Optional

from clisops.core.subset import subset_time, shape_bbox_indexer, subset_gridpoint
from clisops.core.average import average_shape
import intake
import geopandas as gpd
import xarray as xr
import numpy as np
import warnings
from tqdm import tqdm
import pandas as pd
from functools import reduce
import hvplot.xarray
import hvplot.pandas
from dask.distributed import Client
import logging
import warnings

from .spatial import clip_by_polygon, clip_by_point
from .temporal import change_timezone, temporal_aggregation
from .validations import _validate_space_params
from .utils import open_dataset
from .workflows import climate_request
#client = Client()



URL_PATH = 'https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/main.yaml'

__all__ = ["Query"]


class Query:

    """"This is the base class for the datasets extension for xarray"""

    def __init__(self,
                 datasets: Union[str, Dict[str, Union[str, List[str]]]],
                 space: Dict[str, Union[str, List[str]]],
                 time=dict(),
                 catalog_path: str = URL_PATH):
        
        # assert datasets params
        assert _validate_space_params(**space)
        # assert time params

        self.catalog = intake.open_catalog(catalog_path)
        self.datasets = datasets
        self.space = space
        self.time = time
        
        self.load_query(datasets=self.datasets,
                        space=self.space,
                        time=self.time)
    
    def load_query(self,
                   datasets: Union[str, Dict[str, Union[str, List[str]]]],
                   space: Dict[str, Union[str, List[str]]],
                   time):
        
        # Get all datasets in query
        datasets_name = list(datasets.keys())

        # Load data for each dataset
        dsets = []
        # pbar = tqdm(datasets_name)
        for dataset_name in datasets_name:
            # pbar.set_description("Dataset %s" % dataset_name, refresh=True)

            variables_name = self.datasets[dataset_name]['variables']

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
            # Couldn't merge datasets so we pass a dictionary of datasets. 
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
    




