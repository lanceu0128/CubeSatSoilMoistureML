import netCDF4, os, glob, pickle
from pprint import pprint
import numpy as np

# Task: make a SNR and Reflectivity grid at 5km resolution (7200 in longitude and 3600 in latitude)
# conversions between lon/x and lat/y (assuming we need to convert): 
# # lon = (x * 0.05) - 180 
# # lat = (y * 0.05) - 90
# # x = (lon + 180) / 0.05 
# # y = (lat + 90) / 0.05

# initializing grid
snr_grid = np.zeros((3600, 7200))
reflectivity_grid = np.zeros((3600, 7200))

max_lon = 45
min_lon = 45
max_lat = 45
min_lat = 45

def read_file(file_path, snr_grid, reflectivity_grid):
    global max_lon, min_lon, max_lat, min_lat
    nc_file = netCDF4.Dataset(file_path, "r", format="NETCDF4")

    # reading relevant file variables
    reflectivity = nc_file.variables['reflectivity_at_sp'][:]
    snr = nc_file.variables['reflect_snr_at_sp'][:]
    lon = nc_file.variables['sp_lon'][:] 
    lat = nc_file.variables['sp_lat'][:] 

    max_lon = max(max_lon, max(lon)-180)
    min_lon = min(min_lon, min(lon)-180)
    max_lat = max(max_lat, max(lat))
    min_lat = min(min_lat, min(lat))

    for i in range(len(reflectivity)):
        x = int((lon[i] - 180) / 0.05)
        y = int(lat[i] / 0.05)

        print(lon[i]-180, lat[i], snr[i])

        snr_grid[y][x] = snr[i] # y prior to x because python accesses rows before columns
        reflectivity_grid[y][x] = reflectivity[i]

    nc_file.close()

if __name__ == "__main__":
    directory = '/data01/jyin/SPIRE/RAW/2024/20240610'

    for root, dirs, files in os.walk(directory):
        for i, file in enumerate(files):
            if file.endswith('.nc'):
                if (i % 100 == 0):
                    print(f"Reading file {i}")            
                file_path = os.path.join(root, file)
                read_file(file_path, snr_grid, reflectivity_grid)    

    snr_grid = np.nan_to_num(snr_grid)
    reflectivity_grid = np.nan_to_num(reflectivity_grid)
    print(max_lon, min_lon, max_lat, min_lat)
        
    with open('/data01/lpu/snr_grid.pkl', 'wb') as f:
        pickle.dump(snr_grid, f)
    with open('/data01/lpu/reflectivity_grid.pkl', 'wb') as f:
        pickle.dump(reflectivity_grid, f)