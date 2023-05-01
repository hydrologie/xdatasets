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
                         dataset_name,
                         spatial_agg):
    
    ds_new = xr.Dataset(attrs=ds.attrs)
    ds_list = []

    pbar = tqdm(ds.keys())
    for var in pbar:
        pbar.set_description(f"Temporal operations: processing {var} with {dataset_name}")
        # Verify if requested timestep is higher or lower or equal to dataset's native timestep

        # if requested timestep is higher 
        if 'aggregation' in time and var in time['aggregation'].keys():
            operation = time['aggregation'][var] if var in time['aggregation'].keys() else None
            operation = operation if isinstance(operation, list)  else [operation]
            oper_list = []
            for oper in operation:
                var_name = f"{var}_{oper.__name__}"
                da = ds[var].resample(time=time['timestep']).reduce(oper, dim='time').expand_dims({'time_agg':[oper.__name__],
                                                                                                   'spatial_agg': [spatial_agg],
                                                                                                   'timestep': [time['timestep']]})
                #da = da.transpose('id','time', 'timestep','time_agg','spatial_agg')
                oper_list.append(da)

            # ds_new = ds_new.merge(xr.concat(oper_list, dim='time_agg'))
            ds_list.append(xr.concat(oper_list, dim='time_agg'))

        else:
            try:
                ds_new = ds_new.merge(ds[var])
            except:
                pass
            # TODO: return error if cannot merge for inconstitant query
    
    if ds_list:
        ds_new = xr.merge(ds_list)



        # if requested timestep is lower
        # bfill the timestep and add a warning

        # if requested timestep is equal : do nothing
   # print(ds_new.tp)

    return ds_new


    