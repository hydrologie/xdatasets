import fnmatch
import itertools
import warnings

import pandas as pd
import xarray as xr
from clisops.core.subset import subset_time

from .spatial import clip_by_bbox, clip_by_point, clip_by_polygon
from .temporal import (
    ajust_dates,
    change_timezone,
    minimum_duration,
    temporal_aggregation,
)
from .utils import open_dataset


def climate_request(dataset_name, variables, space, time, catalog):
    ds = open_dataset(dataset_name, catalog)

    rename_dict = {
        # dim labels (order represents the priority when checking for the dim labels)
        "longitude": ["lon", "long", "x"],
        "latitude": ["lat", "y"],
    }

    dims = list(ds.dims)
    for key, values in rename_dict.items():
        for value in values:
            if value in dims:
                ds = ds.rename({value: key})

    try:
        ds = ds[variables]
    except:
        pass

    # Ajust timezone and then slice time dimension before moving on with spatiotemporal operations
    if time["timezone"] is not None:
        try:
            # Assume UTC for now, will change when metadata database in up and running
            ds = change_timezone(ds, "UTC", time["timezone"])
        except:
            pass  # replace by error

    if time["start"] is not None or time["end"] is not None:
        try:
            start_time = time["start"] if "start" in time else None
            end_time = time["end"] if "end" in time else None
            ds = subset_time(ds, start_date=start_time, end_date=end_time)
        except:
            pass  # replace by error

    # Spatial operations
    if space["clip"] == "polygon":
        spatial_agg = "polygon"
        ds = clip_by_polygon(ds, space, dataset_name).load()

    elif space["clip"] == "point":
        spatial_agg = "point"
        ds = clip_by_point(ds, space, dataset_name).load()

    elif space["clip"] == "bbox":
        spatial_agg = "polygon"
        ds = clip_by_bbox(ds, space, dataset_name).load()

    if time["timestep"] is not None and time["aggregation"] is not None:
        ds = temporal_aggregation(ds, time, dataset_name, spatial_agg)
    # Add source name to dataset
    # np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    ds = ds.assign_coords(source=("source", [dataset_name]))

    # This is painfully slow if the dataset is large enough and will be commented for now
    # for var in ds.keys():
    #     ds[var] = ds[var].expand_dims("source", axis=-1)
    return ds


def gis_request(dataset_name, variables, space, time, catalog, **kwargs):
    # This parameter should be set in the catalog
    unique_id = catalog["geography"][dataset_name].metadata["unique_id"]

    if any(kwargs):
        ds = hydrometric_request(
            dataset_name.replace("_polygons", ""),
            variables,
            space,
            time,
            catalog,
            **kwargs,
        )
        filters = {"filters": [(unique_id, "in", tuple(ds.id.values.tolist()))]}
    else:
        filters = None
        warnings.warn(
            "No filters fetches the complete dataset (few minutes). Use filters to expedite data retrieval."
        )

    gdf = (
        catalog["geography"][dataset_name](geopandas_kwargs=filters)
        .read()
        .infer_objects()
        .set_index(unique_id)
    )
    gdf.index = gdf.index.astype("str")

    return gdf


def hydrometric_request(dataset_name, variables, space, time, catalog, **kwargs):
    ds = open_dataset(dataset_name, catalog)

    try:
        ds = ds.sel(variable=variables)
        ds = ds[variables]
    except:
        pass

    for key, value in kwargs.items():
        try:
            if isinstance(value, str):
                value = [value]

            # If user provided a wildcard to match a pattern for a specific dimension
            if any("*" in pattern or "?" in pattern for pattern in value):
                value = list(
                    itertools.chain.from_iterable(
                        [fnmatch.filter(ds[key].data, val) for val in value]
                    )
                )

            ds = ds.where(ds[key].isin(value).load(), drop=True)
        except:
            # Add warning
            pass

    # TODO: to implement this feature, We will need the timezone as a coords for each id

    # # Ajust timezone and then slice time dimension before moving on with spatiotemporal operations
    # if time["timezone"] != None:
    #     try:
    #         # Assume UTC for now, will change when metadata database in up and running
    #         ds = change_timezone(ds, 'UTC', time['timezone'])
    #     except:
    #         pass # replace by error

    if time["start"] is not None or time["end"] is not None:
        try:
            start_time = time["start"] if "start" in time else None
            end_time = time["end"] if "end" in time else None
            ds = subset_time(ds, start_date=start_time, end_date=end_time)
        except:
            pass  # replace by error

    # # Spatial operations
    # TODO : Find all stations within a gdf's mask
    # if space['clip'] == 'polygon':
    #     ds = clip_by_polygon(ds, space, dataset_name).load()

    # TODO : find the closest station to each point(s)
    # elif space['clip'] == 'point':
    #     ds = clip_by_point(ds, space, dataset_name).load()

    # TODO : Convert gdf's mask to bbox, find all stations within that bbox and apply function below
    # elif space['clip'] == 'bbox':
    #     ds = clip_by_bbox(ds, space, dataset_name).load()

    if time["start"] is not None or time["end"] is not None:
        ds = ajust_dates(ds, time)

    if time["minimum_duration"] is not None:
        ds = minimum_duration(ds, time)

    if time["timestep"] is not None and time["aggregation"] is not None:
        if pd.Timedelta(1, unit=time["timestep"]) > pd.Timedelta(
            1, unit=xr.infer_freq(ds.time)
        ):
            spatial_agg = "polygon"
            ds = temporal_aggregation(ds, time, dataset_name, spatial_agg)

    # Remove all dimension values that are not required anymore after previous filetring
    # This returns a cleaner dataset at the cost of a compute
    # _to_stack = []
    # for dim in ds.dims:
    #     if len(ds[dim]) >1:
    #         _to_stack.append(dim)
    # print('stack')
    # ds = ds.stack(stacked=_to_stack)

    ## Drop the pixels that only have NA values.
    # print('dropna')
    # ds = ds.dropna("stacked", how="all")

    # print('unstack')
    # ds = ds.unstack('stacked')

    return ds


def user_provided_dataset(dataset_name, variables, space, time, ds):
    try:
        ds = ds[variables]
    except:
        pass

    # TODO: to implement this feature, We will need the timezone as a coords for each id

    # # Ajust timezone and then slice time dimension before moving on with spatiotemporal operations
    # if time["timezone"] != None:
    #     try:
    #         # Assume UTC for now, will change when metadata database in up and running
    #         ds = change_timezone(ds, 'UTC', time['timezone'])
    #     except:
    #         pass # replace by error

    if time["start"] is not None or time["end"] is not None:
        try:
            start_time = time["start"] if "start" in time else None
            end_time = time["end"] if "end" in time else None
            ds = subset_time(ds, start_date=start_time, end_date=end_time)
        except:
            pass  # replace by error

    # Spatial operations
    if space["clip"] == "polygon":
        spatial_agg = "polygon"
        ds = clip_by_polygon(ds, space, dataset_name).load()

    elif space["clip"] == "point":
        spatial_agg = "point"
        ds = clip_by_point(ds, space, dataset_name).load()

    elif space["clip"] == "bbox":
        spatial_agg = "polygon"
        ds = clip_by_bbox(ds, space, dataset_name).load()

    if time["timestep"] is not None and time["aggregation"] is not None:
        if pd.Timedelta(1, unit=time["timestep"]) > pd.Timedelta(
            1, unit=xr.infer_freq(ds.time)
        ):
            ds = temporal_aggregation(ds, time, dataset_name, spatial_agg)
    # Add source name to dataset
    # np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    ds = ds.assign_coords(source=("source", [dataset_name]))
    # for var in ds.keys():
    #     ds[var] = ds[var].expand_dims("source", axis=-1)

    return ds
