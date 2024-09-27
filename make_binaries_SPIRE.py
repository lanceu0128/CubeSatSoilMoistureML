import netCDF4, os, glob, pickle, re
from pathlib import Path
from pprint import pprint
import numpy as np

def read_file(file, grid_snr, grid_refl, grid_count_snr, grid_count_refl):
    nc_file = netCDF4.Dataset(file, "r", format="NETCDF4")

    refl = nc_file.variables['reflectivity_at_sp'][:]
    snr = nc_file.variables['reflect_snr_at_sp'][:]
    lon = nc_file.variables['sp_lon'][:]
    lat = nc_file.variables['sp_lat'][:]

    x = (lon / 0.05).astype(int)
    y = ((lat + 90) / 0.05).astype(int)

    x = np.clip(x, 0, 7199)
    y = np.clip(y, 0, 3599)

    valid_snr = ~np.ma.getmaskarray(snr) & ~np.isnan(snr)
    valid_refl = ~np.ma.getmaskarray(refl) & ~np.isnan(refl)

    grid_snr[y[valid_snr], x[valid_snr]] = snr[valid_snr]
    grid_refl[y[valid_refl], x[valid_refl]] = refl[valid_refl]
    
    grid_count_snr[y[valid_snr], x[valid_snr]] += 1
    grid_count_refl[y[valid_refl], x[valid_refl]] += 1

    nc_file.close()
    
    return grid_snr, grid_refl, grid_count_snr, grid_count_refl

if __name__ == "__main__":
    directory = Path('/data01/jyin/SPIRE/RAW/2024')

    for i, folder in enumerate(directory.iterdir()):
        if folder.is_dir():
            print(f"Processing date: {folder.name}")
            snr_grid = np.zeros((3600,7200))
            refl_grid = np.zeros((3600,7200))
            count_snr_grid = np.zeros((3600,7200))
            count_refl_grid = np.zeros((3600,7200))

            for j, file in enumerate(folder.iterdir()):
                if file.is_file() and file.suffix == '.nc':        
                    if (j % 250 == 0):
                        print(f"- Reading file #{j}")

                        snr_grid, refl_grid, count_snr_grid, count_refl_grid = read_file(file, snr_grid, refl_grid, count_snr_grid, count_refl_grid)

            mask_snr = count_snr_grid > 0
            mask_refl = count_refl_grid > 0
        
            snr_grid[mask_snr] = snr_grid[mask_snr] / count_snr_grid[mask_snr]
            refl_grid[mask_refl] = refl_grid[mask_refl] / count_refl_grid[mask_refl]

            snr_grid[~mask_snr] = -9999
            refl_grid[~mask_refl] = -9999

            with open(f'/data01/lpu/SPIRE/SNR/2024/{folder.name}.pkl', 'wb') as f:
                pickle.dump(snr_grid, f)
            with open(f'/data01/lpu/SPIRE/reflectivity/2024/{folder.name}.pkl', 'wb') as f:
                pickle.dump(refl_grid, f)