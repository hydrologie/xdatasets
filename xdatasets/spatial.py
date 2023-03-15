from typing import Sequence, Tuple, Union, Dict, List, Optional

from clisops.core.subset import subset_shape, subset_time, create_mask, shape_bbox_indexer, create_weight_masks, subset_gridpoint
from clisops.core.average import average_shape
import xarray as xr
from tqdm import tqdm
import logging


def get_weight_masks(da, geom):
    mask = create_weight_masks(da,
            poly=geom)
    da['weights'] = mask.squeeze()
    da = da.where(da.weights>0, drop=True)
    return da

def bbox_ds(ds_copy, geom):
    indexer = shape_bbox_indexer(ds_copy, geom)
    da = ds_copy.isel(indexer)
    da = da.chunk({'latitude':-1, 'longitude':-1})
    return da


def clip_by_bbox(ds,
                 space,
                 dataset_name
                 ):
    logging.info(f"Spatial operations: processing bbox with {dataset_name}")
    indexer = shape_bbox_indexer(ds, space['geometry'])
    ds_copy = ds.isel(indexer).copy()
    return ds_copy
    

def clip_by_polygon(ds,
                    space,
                    dataset_name
                    ):
    indexer = shape_bbox_indexer(ds, space['geometry'])
    ds_copy = ds.isel(indexer).copy()
    
    arrays = []
    pbar = tqdm(space['geometry'].iterrows())
    for idx, row in pbar:
        item = row[space['unique_id']] if space['unique_id'] != None and space['unique_id'] in row else idx
        pbar.set_description(f"Spatial operations: processing polygon {item} with {dataset_name}")

        geom = space['geometry'].iloc[[idx]]
        da = bbox_ds(ds_copy, geom)

        # Average data array over shape
        if space['averaging'] is True:            
            da = average_shape(da, shape=geom)
        else:
            da = get_weight_masks(da, geom)
        arrays.append(da)
    data = xr.concat(arrays, dim='geom')

    if 'unique_id' in space:
        try:
            data = data.swap_dims({"geom": space["unique_id"]})
            data = data.drop('geom')

            if space['unique_id'] not in data.coords:
                data = data.assign_coords({space['unique_id']: (space['unique_id'],
                                                        space['geometry'][space['unique_id']])})   
        except:
            pass
    return data


def clip_by_point(ds, space, dataset_name):

    logger = logging.getLogger()
    logging.info(f"Spatial operations: processing points with {dataset_name}")

    lat,lon = zip(*space['geometry'].values())
    data = subset_gridpoint(ds.rename({'latitude':'lat', 'longitude':'lon'}), lon=list(lon), lat=list(lat))
    data = data.rename({'lat':'latitude', 'lon':'longitude'})

    data = data.assign_coords({'site': ('site', list(space['geometry'].keys()))})   
    return data