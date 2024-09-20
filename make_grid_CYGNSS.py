import netCDF4
from pathlib import Path
import numpy as np
import pickle

# Task: make a grid of CYGNSS SNR and Reflectivity data for comparison and validation of SPIRE data
# very few comments because the logic is almost exactly the same as make_grid.py  

def read_file(file, grid_snr, grid_reflectivity):
    nc_file = netCDF4.Dataset(file, "r", format="NETCDF4")
    
    # lon ~ [0, 360], lat ~ [-45, 45]
    reflectivity = nc_file.variables['reflectivity_peak'][:]
    snr = nc_file.variables['ddm_snr'][:]
    lon = nc_file.variables['sp_lon'][:]
    lat = nc_file.variables['sp_lat'][:]

    x = (lon / 0.05).astype(int)
    y = ((lat + 45) / 0.05).astype(int) # about half of the range

    x = np.clip(x, 0, 7199)
    y = np.clip(y, 0, 1799)

    valid_snr = ~np.ma.getmaskarray(snr) & ~np.isnan(snr)
    valid_reflectivity = ~np.ma.getmaskarray(reflectivity) & ~np.isnan(reflectivity)

    grid_snr[y[valid_snr], x[valid_snr]] = snr[valid_snr]

    grid_reflectivity[y[valid_reflectivity], x[valid_reflectivity]] = reflectivity[valid_reflectivity]

    nc_file.close()
    
    return grid_snr, grid_reflectivity


if __name__ == "__main__":
    directory = Path('/data01/jyin/CYGNSS/data/V3.2/2023/')
    month = "-e202304"

    # lat ~ [-45, 45], so we need to have 1800 lat values in the grid to keep the same resolution
    snr_grid = np.full((1800, 7200), -9999)
    reflectivity_grid = np.full((1800, 7200), -9999)

    for folder in directory.iterdir():
        if folder.is_dir():            
            for file in folder.iterdir():
                if file.is_file() and file.suffix == '.nc' and month in file.name:
                    print(f"Reading file: {file.as_posix()}")
                    snr_grid, reflectivity_grid = read_file(file, snr_grid, reflectivity_grid)
 
    snr_grid = np.nan_to_num(snr_grid, nan=-9999)
    reflectivity_grid = np.nan_to_num(reflectivity_grid, nan=-9999)

    with open('/data01/lpu/snr_grid_cygnss.pkl', 'wb') as f:
        pickle.dump(snr_grid, f)
    with open('/data01/lpu/reflectivity_grid_cygnss.pkl', 'wb') as f:
        pickle.dump(reflectivity_grid, f)