# ///////////////////////
# BRAN2020_quantile.py
# 6 May 2024
#////////////////////////
# --------- packages --------------
import intake
import xarray as xr
import pandas as pd
import numpy as np
from dask.distributed import Client, LocalCluster
import dask
import datetime
import os
import configparser
import sys

def main():
    """
    spin up cluster & do the work   
    """
    print("importing functions ...")
    # Append the directory of the module to sys.path - import functions
    sys.path.append('/g/data/es60/users/thomas_moore/code/Climatology-generator-demo/src/')
    import bran2020_demo_functions as my_tools

    print("Spinning up a dask cluster...")
    # -----------  cluster -----------------------
    import dask
    from dask.distributed import Client, LocalCluster

    
    cluster = LocalCluster(n_workers=48,threads_per_worker=1,processes=True)
    client = Client(cluster)
    print(client)
    # ----- catalog ----
    #
    config = configparser.ConfigParser()
    config.read('/g/data/es60/users/thomas_moore/code/BRAN2020-intake-catalog/config.ini')
    catalog_path = config.get('paths', 'catalog_path')
    #
    BRAN2020_catalog = intake.open_esm_datastore(catalog_path+'BRAN2020.json',columns_with_iterables=['variable'])
    var_request_list = ['salt']
    var = var_request_list[0]
    print("variable requested: "+var)
    time_period_request_list = ['daily']
    search = BRAN2020_catalog.search(variable=var,time_period=time_period_request_list)
    xarray_open_kwargs = {"chunks": {"Time": -1,'st_ocean':10}}
    DS=search.to_dask(xarray_open_kwargs=xarray_open_kwargs)
    my_tools.print_chunks(DS[var])
    # run quantile_monthclim
    quantile_monthclim_ds = my_tools.quantile_monthclim(DS,var_name=var,time_dim='Time',skipna_flag=False)
    print(quantile_monthclim_ds.nbytes/1e9)
    #convert float64 quantile to float32
    for var in quantile_monthclim_ds.data_vars:
        quantile_monthclim_ds[var] = quantile_monthclim_ds[var].astype('float32')
    # write to netcdf
    results_path = '/g/data/es60/users/thomas_moore/clim_demo_results/daily/draft_delivery/quantile_PBS/'
    results_file = 'BRAN2020_quantile_monthclim_'+var+'.nc'
    print("writing to the netcdf file for : "+var+" ....")
    quantile_monthclim_ds.to_netcdf(results_path+results_file,engine='netcdf4')
    print("netcdf written: "+var)
    #done
    print(">>>>> DONE with quantile calc and write to netcdf for: "+var)

if __name__ == "__main__":
    main()