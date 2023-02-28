import datetime
import time


def get_julian_day(month, day, year = None):
    """
    Return julian day for a specified date, if year is not specified, uses curent year

    Parameters
    ----------
    month : int
        integer of the target month
        
    day : int
        integer of the target day
        
    year : int
        integer of the target year

    Returns
    -------
    int
        julian day (1 - 366)
        
    Examples
    --------
    >>> import xarray as xr
    >>> cehq_data_path = '/dbfs/mnt/devdlzxxkp01/datasets/xdatasets/tests/cehq/zarr'
    >>> ds = xr.open_zarr(cehq_data_path, consolidated=True)
    >>> donnees = Data(ds)
    >>> jj = donnees.get_julian_day(month = 9, day = 1)
    >>> jj: 244
    >>> jj = donnees.get_julian_day(month = 9, day = 1, year = 2000)
    >>> jj: 245
    """    
    if year is None:
        year = datetime.date.today().year

    return datetime.datetime(year, month, day).timetuple().tm_yday



def tic():
    #Homemade version of matlab tic and toc functions
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()

def toc(tag = ""):
    if 'startTime_for_tictoc' in globals():
        print(tag + " Elapsed time is " + str(time.time() - startTime_for_tictoc) + " seconds.")
    else:
        print("Toc: start time not set")