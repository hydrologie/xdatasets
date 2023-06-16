from typing import Sequence, Tuple, Union, Dict, List, Optional

from clisops.core.subset import subset_shape, subset_time, create_mask, shape_bbox_indexer, subset_gridpoint
from clisops.core.average import average_shape
import xarray as xr
from tqdm import tqdm
import logging
import xagg_no_xesmf_deps as xa
import pandas as pd

from .utils import HiddenPrints


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
    
def create_weights_mask(da, poly):
    
    weightmap = xa.pixel_overlaps(da, poly, subset_bbox=True)

    pixels = pd.DataFrame(index=weightmap.agg['pix_idxs'][0],
                          data=list(map(list, weightmap.agg['coords'][0])),
                          columns=['latitude','longitude']
                         )

    weights = pd.DataFrame(index=weightmap.agg['pix_idxs'][0],
                 data=weightmap.agg['rel_area'][0][0].tolist(),
                 columns=['weights'])


    df = pd.merge(pixels, weights, left_index=True, right_index=True)
    return df.set_index(['latitude', 'longitude']).to_xarray()

def aggregate(ds_in, ds_weights):
    return (ds_in*ds_weights.weights).sum(['latitude','longitude'], min_count=1)


def clip_by_polygon(ds,
                    space,
                    dataset_name
                    ):
    # We are not using clisops for weighted averages because it is too unstable for now and requires conda environment.
    # We use a modified version of the xagg package from which we have removed the xesmf/esmpy dependency


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
            #da = average_shape(da, shape=geom)
        with HiddenPrints():
            ds_weights  = create_weights_mask(da.isel(time=0), geom)
        if space['averaging'] is True:   
            da = aggregate(da, ds_weights)
        else:
            da = xr.merge([da, ds_weights])
            da = da.where(da.weights.notnull(), drop=True)
        da = da.expand_dims({"geom": geom.index.values})
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

    #TODO : adapt logic for coordinate names

    logger = logging.getLogger()
    logging.info(f"Spatial operations: processing points with {dataset_name}")

    lat,lon = zip(*space['geometry'].values())
    data = subset_gridpoint(ds.rename({'latitude':'lat', 'longitude':'lon'}), lon=list(lon), lat=list(lat))
    data = data.rename({'lat':'latitude', 'lon':'longitude'})

    data = data.assign_coords({'site': ('site', list(space['geometry'].keys()))})   
    return data