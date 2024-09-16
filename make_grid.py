import netCDF4, os, glob, pickle
from pathlib import Path
from pprint import pprint
import numpy as np

# Task: make SNR and Reflectivity grids at 5km resolution (7200 in longitude and 3600 in latitude)

# reads a given NetCDF4 file and updates the SNR and Reflectivity grid arguments with the values
def read_file(file, grid_snr, grid_reflectivity):
    nc_file = netCDF4.Dataset(file, "r", format="NETCDF4")

    # variables in 1D arrays; we use the lon and lat values to locate the Reflectivity and SNR values 
    reflectivity = nc_file.variables['reflectivity_at_sp'][:]
    snr = nc_file.variables['reflect_snr_at_sp'][:]
    lon = nc_file.variables['sp_lon'][:]
    lat = nc_file.variables['sp_lat'][:]

    for i in range(len(reflectivity)):
        # the lon and lat values in the files range from [0, 360] and [-90, 90] respectively
        # we convert to [0, 360] and [0, 180] first to avoid negatives being interpreted incorrectly as XY
        # when creating the graph we interpret the coordinates as [-180, 180] and [-90, 90]
        x = int((lon[i]) / 0.05)
        y = int((lat[i] + 90) / 0.05)

        # the prior conversions allow for 7200 and 3600 coordinates which don't fit into the grid 
        x = max(min(x, 7199), 0)
        y = max(min(y, 3599), 0)

        # the data contains masked and NaN values that we want to avoid 
        if not np.ma.is_masked(snr[i]) and not np.isnan(snr[i]):
            # y comes before x because python arrays are accessed with rows before cols
            grid_snr[y][x] = snr[i]

        if not np.ma.is_masked(reflectivity[i]) and not np.isnan(reflectivity[i]):
            grid_reflectivity[y][x] = reflectivity[i]

    nc_file.close()
    
    return grid_snr, grid_reflectivity

if __name__ == "__main__":
    # this folder contains all of our data in subfolders for a given date (YYYYMMDD)
    directory = Path('/data01/jyin/SPIRE/RAW/2024')
    # the month we want to grab data for
    month = '202404'

    # default values are -9999 so that we can identify unfilled values later easily
    snr_grid = np.full((3600, 7200), -9999)
    reflectivity_grid = np.full((3600, 7200), -9999)

    # walk through every date folder and process anything from given month
    for i, folder in enumerate(directory.iterdir()):
        if folder.is_dir():
            if folder.name.startswith(month):
                print(f"Processing date: {folder.name}")
                # each date folder has numerous NetCDF4 files that are to be combined for our final grid
                for j, file in enumerate(folder.iterdir()):
                    if file.is_file() and file.suffix == '.nc':        
                        if (j % 250 == 0):
                            print(f"- Reading file #{j}")
                            print(f"- SNR Values above 0: {np.sum(snr_grid > 0)}")  

                        snr_grid, reflectivity_grid = read_file(file, snr_grid, reflectivity_grid)  

    # probably not necessary because we check for non-numeric values in read_file(), but good practice
    snr_grid = np.nan_to_num(snr_grid, nan=-9999)
    reflectivity_grid = np.nan_to_num(reflectivity_grid, nan=-9999)

    # pickle files are nice
    with open('/data01/lpu/snr_grid.pkl', 'wb') as f:
        pickle.dump(snr_grid, f)
    with open('/data01/lpu/reflectivity_grid.pkl', 'wb') as f:
        pickle.dump(reflectivity_grid, f)