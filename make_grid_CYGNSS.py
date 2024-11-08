import netCDF4
from pathlib import Path
import numpy as np
import pickle
from datetime import datetime
from collections import Counter

# Task: make a grid of CYGNSS SNR and Reflectivity data for comparison and validation of SPIRE data
# very few comments because the logic is almost exactly the same as make_grid.py  

def read_file(file, grid_snr, grid_refl, grid_count_snr, grid_count_refl):
    nc_file = netCDF4.Dataset(file, "r", format="NETCDF4")
    
    # Read variables from the netCDF file
    refl = nc_file.variables['reflectivity_peak'][:]
    snr = nc_file.variables['ddm_snr'][:]
    lon = nc_file.variables['sp_lon'][:]
    lat = nc_file.variables['sp_lat'][:]
    quality = nc_file.variables['quality_flags'][:]
    quality_2 = nc_file.variables['quality_flags_2'][:]

    x = (lon / 0.05).astype(int)
    y = ((lat + 45) / 0.05).astype(int)  # about half of the range

    x = np.clip(x, 0, 7199)

    valid_quality = ((((quality & 2048) == 0) | ((quality & 4096) == 0)) & ((quality_2 & 2048) == 0))
    valid_quality = ((quality & 1) == 0) | ((quality_2 & 2048) == 0)
    valid_snr = ~np.ma.getmaskarray(snr) & ~np.isnan(snr) & valid_quality
    valid_refl = ~np.ma.getmaskarray(refl) & ~np.isnan(refl) & valid_quality & (snr <= 2)

    grid_snr[y[valid_snr], x[valid_snr]] += snr[valid_snr]
    grid_count_snr[y[valid_snr], x[valid_snr]] += 1

    grid_refl[y[valid_refl], x[valid_refl]] += refl[valid_refl]
    grid_count_refl[y[valid_refl], x[valid_refl]] += 1

    nc_file.close()
    
    return grid_snr, grid_refl, grid_count_snr, grid_count_refl

if __name__ == "__main__":
    directory = Path('/data01/jyin/CYGNSS/data/V3.2/2024/')

    # data for comparison with SPIRE
    start_date = datetime.strptime("20240125", "%Y%m%d")
    end_date = datetime.strptime("20240602", "%Y%m%d")

    # lat ~ [-45, 45], so we need to have 1800 lat values in the grid to keep the same resolution
    snr_grid = np.zeros((1800,7200))
    refl_grid = np.zeros((1800,7200))
    count_snr_grid = np.zeros((1800,7200))
    count_refl_grid = np.zeros((1800,7200))

    for folder in directory.iterdir():
        if folder.is_dir():
            for file in folder.iterdir():
                if file.is_file() and file.suffix == '.nc':
                    date_str = file.name.split("-e")[-1][:8]
                    file_date = datetime.strptime(date_str, "%Y%m%d")

                    if start_date <= file_date <= end_date:
                        print(f"Reading file: {file.as_posix()}")
                        snr_grid, refl_grid, count_snr_grid, count_refl_grid = read_file(file, snr_grid, refl_grid, count_snr_grid, count_refl_grid)

    mask_snr = count_snr_grid > 0
    mask_refl = count_refl_grid > 0
 
    snr_grid[mask_snr] = snr_grid[mask_snr] / count_snr_grid[mask_snr]
    refl_grid[mask_refl] = refl_grid[mask_refl] / count_refl_grid[mask_refl]

    snr_grid[~mask_snr] = -9999
    refl_grid[~mask_refl] = -9999

    with open('/data01/lpu/cygnss_snr_grid.pkl', 'wb') as f:
        pickle.dump(snr_grid, f)
    with open('/data01/lpu/cygnss_reflectivity_grid.pkl', 'wb') as f:
        pickle.dump(refl_grid, f)