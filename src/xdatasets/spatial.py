import logging
import warnings

import pandas as pd
import xarray as xr
from clisops.core.subset import shape_bbox_indexer, subset_gridpoint
from tqdm.auto import tqdm

from .utils import HiddenPrints

try:
    import xagg as xa
except ImportError:
    warnings.warn("xagg is not installed. Please install it with `pip install xagg`")
    xa = None


def bbox_ds(ds_copy, geom):
    indexer = shape_bbox_indexer(ds_copy, geom)
    da = ds_copy.isel(indexer)
    da = da.chunk({"latitude": -1, "longitude": -1})
    return da


def clip_by_bbox(ds, space, dataset_name):
    logging.info(f"Spatial operations: processing bbox with {dataset_name}")
    indexer = shape_bbox_indexer(ds, space["geometry"])
    ds_copy = ds.isel(indexer).copy()
    return ds_copy


def create_weights_mask(da, poly):
    if xa is None:
        raise ImportError(
            "xagg is not installed. Please install it with `pip install xagg`"
        )

    weightmap = xa.pixel_overlaps(da, poly, subset_bbox=True)

    pixels = pd.DataFrame(
        index=weightmap.agg["pix_idxs"][0],
        data=list(map(list, weightmap.agg["coords"][0])),
        columns=["latitude", "longitude"],
    )

    weights = pd.DataFrame(
        index=weightmap.agg["pix_idxs"][0],
        data=weightmap.agg["rel_area"][0][0].tolist(),
        columns=["weights"],
    )

    df = pd.merge(pixels, weights, left_index=True, right_index=True)
    return df.set_index(["latitude", "longitude"]).to_xarray()


def aggregate(ds_in, ds_weights):
    return (ds_in * ds_weights.weights).sum(["latitude", "longitude"], min_count=1)


def clip_by_polygon(ds, space, dataset_name):
    # We are not using clisops for weighted averages because it is too unstable for now.
    # We use the xagg package instead.

    indexer = shape_bbox_indexer(ds, space["geometry"])
    ds_copy = ds.isel(indexer).copy()

    arrays = []
    pbar = tqdm(space["geometry"].iterrows(), position=0, leave=True)
    for idx, row in pbar:
        item = (
            row[space["unique_id"]]
            if space["unique_id"] is not None and space["unique_id"] in row
            else idx
        )
        pbar.set_description(
            f"Spatial operations: processing polygon {item} with {dataset_name}"
        )

        geom = space["geometry"].iloc[[idx]]
        da = bbox_ds(ds_copy, geom)

        # Average data array over shape
        # da = average_shape(da, shape=geom)
        with HiddenPrints():
            ds_weights = create_weights_mask(da.isel(time=0), geom)
        if space["averaging"] is True:
            da_tmp = aggregate(da, ds_weights)
            for var in da_tmp.variables:
                da_tmp[var].attrs = da[var].attrs
            da = da_tmp
        else:
            da = xr.merge([da, ds_weights])
            da = da.where(da.weights.notnull(), drop=True)
        da = da.expand_dims({"geom": geom.index.values})
        arrays.append(da)

    data = xr.concat(arrays, dim="geom")

    if "unique_id" in space:
        try:
            data = data.swap_dims({"geom": space["unique_id"]})
            data = data.drop_vars("geom")

            if space["unique_id"] not in data.coords:
                data = data.assign_coords(
                    {
                        space["unique_id"]: (
                            space["unique_id"],
                            space["geometry"][space["unique_id"]],
                        )
                    }
                )
            data[space["unique_id"]].attrs["cf_role"] = "timeseries_id"
        except KeyError:
            pass
    return data


def clip_by_point(ds, space, dataset_name):
    # TODO : adapt logic for coordinate names

    logging.info(f"Spatial operations: processing points with {dataset_name}")

    lat, lon = zip(*space["geometry"].values())
    data = subset_gridpoint(
        ds.rename({"latitude": "lat", "longitude": "lon"}), lon=list(lon), lat=list(lat)
    )
    data = data.rename({"lat": "latitude", "lon": "longitude"})

    data = data.assign_coords({"site": ("site", list(space["geometry"].keys()))})

    data["site"].attrs["cf_role"] = "timeseries_id"

    return data
