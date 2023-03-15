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
from dask.distributed import Client
import logging

from .spatial import clip_by_polygon, clip_by_point, clip_by_bbox
from .temporal import change_timezone, temporal_aggregation
from .validations import _validate_space_params
from .utils import open_dataset


def climate_request(dataset_name,
                    variables,
                    space,
                    time,
                    catalog):

    ds = open_dataset(dataset_name, catalog)

    try:
        ds = ds[variables]
    except:
        pass

    # Ajust timezone and then slice time dimension before moving on with spatiotemporal operations
    if time["timezone"] != None:
        try:
            # Assume UTC for now, will change when metadata database in up and running
            ds = change_timezone(ds, 'UTC', time['timezone'])
        except:
            pass # replace by error

    if time["start"] != None or time["end"] != None:
        try:
            start_time = time['start'] if 'start' in time else None
            end_time = time['end'] if 'end' in time else None
            ds = subset_time(ds, start_date=start_time, end_date=end_time)
        except:
            pass # replace by error

    # Spatial operations
    if space['clip'] == 'polygon':
        ds = clip_by_polygon(ds, space, dataset_name).load()

    elif space['clip'] == 'point':
        ds = clip_by_point(ds, space, dataset_name).load()

    elif space['clip'] == 'bbox':
        ds = clip_by_bbox(ds, space, dataset_name).load()
        
    if time["timestep"] != None and time['aggregation'] != None:
        ds = temporal_aggregation(ds,
                                  time,
                                  dataset_name)
    # Add source name to dataset
    #np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    ds = ds.assign_coords(source=("source", [dataset_name]))
    for var in ds.keys():
        ds[var] = ds[var].expand_dims("source", axis=-1)
    return ds