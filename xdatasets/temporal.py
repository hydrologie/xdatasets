import xarray as xr
from tqdm import tqdm


def change_timezone(ds, 
                    input_timezone,
                    output_timezone = None
                ):
    if output_timezone == None:
        output_timezone = input_timezone

    time = ds['time'].to_index()
    time_input_tz = time.tz_localize(input_timezone)
    time_output_tz = time_input_tz.tz_convert(output_timezone).tz_localize(None)

    ds = ds.update({'time': time_output_tz})
    ds.attrs['timezone'] = output_timezone
    return ds
    
def temporal_aggregation(ds,
                         time,
                         dataset_name):
    
    ds_new = xr.Dataset(attrs=ds.attrs)

    

    pbar = tqdm(ds.keys())
    for var in pbar:
        pbar.set_description(f"Temporal operations: processing {var} with {dataset_name}")
        try:
            # Verify if requested timestep is higher or lower or equal to dataset's native timestep

            # if requested timestep is higher 
            if 'aggregation' in time:
                operation = time['aggregation'][var] if var in time['aggregation'].keys() else None
                operation = operation if isinstance(operation, list)  else [operation]
                for oper in operation:
                    var_name = f"{var}_{oper.__name__}"
                    ds_new[var_name] = ds[var].resample(time=time['timestep']).reduce(oper, dim='time')
            # if requested timestep is lower
            # bfill the timestep and add a warning

            # if requested timestep is equal : do nothing
        except:
            pass
    return ds_new


    