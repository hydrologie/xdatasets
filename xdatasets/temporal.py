import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm


def change_timezone(ds, input_timezone, output_timezone=None):
    if output_timezone is None:
        output_timezone = input_timezone

    time = ds["time"].to_index()
    time_input_tz = time.tz_localize(input_timezone)
    time_output_tz = time_input_tz.tz_convert(output_timezone).tz_localize(None)

    ds = ds.update({"time": time_output_tz})
    ds.attrs["timezone"] = output_timezone
    return ds


def temporal_aggregation(ds, time, dataset_name, spatial_agg):
    ds_new = xr.Dataset(attrs=ds.attrs)
    ds_list = []

    pbar = tqdm(ds.keys())
    for var in pbar:
        pbar.set_description(
            f"Temporal operations: processing {var} with {dataset_name}"
        )
        # Verify if requested timestep is higher or lower or equal to dataset's native timestep

        # if requested timestep is higher
        if "aggregation" in time and var in time["aggregation"].keys():
            operation = (
                time["aggregation"][var] if var in time["aggregation"].keys() else None
            )
            operation = operation if isinstance(operation, list) else [operation]
            oper_list = []
            for oper in operation:
                # var_name = f"{var}_{oper.__name__}"
                da = (
                    ds[var]
                    .resample(time=time["timestep"])
                    .reduce(oper, dim="time")
                    .expand_dims(
                        {
                            # "time_agg": [oper.__name__],
                            "spatial_agg": [spatial_agg],
                            "timestep": [time["timestep"]],
                        }
                    )
                )
                # da = da.transpose('id','time', 'timestep','time_agg','spatial_agg')
                oper_list.append(da.rename(f"{var}_{oper.__name__}"))

            # ds_new = ds_new.merge(xr.concat(oper_list, dim='time_agg'))
            ds_list.append(xr.merge(oper_list))

        else:
            try:
                ds_new = ds_new.merge(ds[var])
            except:
                pass
            # TODO: return error if cannot merge for inconstant query

    if ds_list:
        ds_new = xr.merge(ds_list)
        # for var in ds_new:
        #     ds_new[var].attrs = ds[var].attrs

        # if requested timestep is lower
        # bfill the timestep and add a warning

        # if requested timestep is equal : do nothing
    # print(ds_new.tp)

    return ds_new


def ajust_dates(ds, time):
    start = time["start"]
    end = time["end"]

    if start is not None:
        ds["start_date"] = xr.where(
            ds.start_date < pd.Timestamp(start),
            np.datetime64(start),
            ds.start_date,
        )

    if end is not None:
        ds["end_date"] = xr.where(
            ds.end_date > pd.Timestamp(end),
            np.datetime64(end),
            ds.end_date,
        )

    return ds


# Only keep ids where at least 15 years of data is available


def minimum_duration(ds, time):
    minimum_duration_value, unit = time["minimum_duration"]

    indexer = (ds.end_date - ds.start_date) > pd.to_timedelta(
        minimum_duration_value, unit=unit
    )

    if indexer.chunks is not None:
        indexer = indexer.compute()

    return ds.where(indexer, drop=True)
