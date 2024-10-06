import netCDF4, os, glob, pickle
from pathlib import Path
from pprint import pprint
import numpy as np

# Task: make SNR and Reflectivity grids at 5km resolution (7200 in longitude and 3600 in latitude)

def read_file(file, grid_snr, grid_refl, grid_count_snr, grid_count_refl):
    nc_file = netCDF4.Dataset(file, "r", format="NETCDF4")

    lon = nc_file.variables['sp_lon'][:]
    lat = nc_file.variables['sp_lat'][:]

    x = (lon / 0.05).astype(int)
    y = ((lat + 90) / 0.05).astype(int)
    x = np.clip(x, 0, 7199)
    y = np.clip(y, 0, 3599)

    if 'reflect_snr_at_sp' in nc_file.variables.keys():
        snr = nc_file.variables['reflect_snr_at_sp'][:]
        
        valid_snr = ~np.ma.getmaskarray(snr) & ~np.isnan(snr)
        
        grid_snr[y[valid_snr], x[valid_snr]] += snr[valid_snr]
        grid_count_snr[y[valid_snr], x[valid_snr]] += 1

    if "reflectivity_at_sp" in nc_file.variables.keys():
        refl = nc_file.variables['reflectivity_at_sp'][:]

        valid_refl = ~np.ma.getmaskarray(refl) & ~np.isnan(refl)

        grid_refl[y[valid_refl], x[valid_refl]] += refl[valid_refl]
        grid_count_refl[y[valid_refl], x[valid_refl]] += 1

    nc_file.close()
    
    return grid_snr, grid_refl, grid_count_snr, grid_count_refl

if __name__ == "__main__":
    # this folder contains all of our data in subfolders for a given date (YYYYMMDD)
    directory = Path('/data01/jyin/SPIRE/RAW/2024')

    # default values are -9999 so that we can identify unfilled values later easily
    # snr_grid and reflectivity_grid will store total values and their # of readings used are stored in the count grids
    # the totals and counts will be used to average the readings after all data is processed 
    snr_grid = np.zeros((3600,7200))
    refl_grid = np.zeros((3600,7200))
    count_snr_grid = np.zeros((3600,7200))
    count_refl_grid = np.zeros((3600,7200))

    # walk through every date folder and process everything inside
    for i, folder in enumerate(directory.iterdir()):
        if folder.is_dir():
            print(f"Processing date: {folder.name}")
            # each date folder has numerous NetCDF4 files that are to be combined for our final grid
            for j, file in enumerate(folder.iterdir()):
                if file.is_file() and file.suffix == '.nc':        
                    if (j % 250 == 0):
                        print(f"- Reading file #{j}")
                        print(f"- SNR Values above 0: {np.sum(snr_grid > 0)}")  

                    try:
                        snr_grid, refl_grid, count_snr_grid, count_refl_grid = read_file(file, snr_grid, refl_grid, count_snr_grid, count_refl_grid)
                    except:
                        print(file.as_posix())
                        
    # only do averages where we found values (avoid dividing by zero error)
    mask_snr = count_snr_grid > 0
    mask_refl = count_refl_grid > 0
 
    # average out data according to total of readings / number of readings
    snr_grid[mask_snr] = snr_grid[mask_snr] / count_snr_grid[mask_snr]
    refl_grid[mask_refl] = refl_grid[mask_refl] / count_refl_grid[mask_refl]

    # set grid spaces where no readings to found to -9999
    snr_grid[~mask_snr] = -9999
    refl_grid[~mask_refl] = -9999

    snr_grid = snr_grid.astype(np.float32)
    refl_grid = refl_grid.astype(np.float32)

    # pickle files are nice
    with open('/data01/lpu/spire_snr_grid.pkl', 'wb') as f:
        pickle.dump(snr_grid, f)
    with open('/data01/lpu/spire_reflectivity_grid.pkl', 'wb') as f:
        pickle.dump(refl_grid, f)