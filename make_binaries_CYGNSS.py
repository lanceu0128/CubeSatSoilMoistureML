
import netCDF4, os, glob, pickle, re
from pathlib import Path
from pprint import pprint
import numpy as np

def read_file(file, grid_snr, grid_refl, grid_count_snr, grid_count_refl):
    nc_file = netCDF4.Dataset(file, "r", format="NETCDF4")

    snr = nc_file.variables['ddm_snr'][:]
    lon = nc_file.variables['sp_lon'][:]
    lat = nc_file.variables['sp_lat'][:]

    x = (lon / 0.05).astype(int)
    y = ((lat + 45) / 0.05).astype(int)
    x = np.clip(x, 0, 7199)

    # the extra y value stuff is due to old CYGNSS files having a full -90 to 90 range
    # we want to simply ignore those for consistency
    valid_snr = ~np.ma.getmaskarray(snr) & ~np.isnan(snr) & (y >= 0) & (y < 1800)

    grid_snr[y[valid_snr], x[valid_snr]] += snr[valid_snr]
    grid_count_snr[y[valid_snr], x[valid_snr]] += 1

    # some old files in the CYGNSS data don't have reflectivity
    # we still want to get SNR values from them so we still process
    if "mss_matchup" not in file.name:
        refl = nc_file.variables['reflectivity_peak'][:]

        valid_refl = ~np.ma.getmaskarray(refl) & ~np.isnan(refl) & (y >= 0) & (y < 1800)

        grid_refl[y[valid_refl], x[valid_refl]] += refl[valid_refl]
        grid_count_refl[y[valid_refl], x[valid_refl]] += 1

    nc_file.close()
    
    return grid_snr, grid_refl, grid_count_snr, grid_count_refl

if __name__ == "__main__":
    # need to iterate through every year, every number, every file
    directory = Path('/data01/jyin/CYGNSS/data/V3.2/')

    # we need to separate the paths by their date so we can get a binary of the entire date's grid
    paths_for_date = {}

    for year in directory.iterdir():
        if year.name == "2018":
            continue

        if not year.is_dir():
            continue            
        
        for folder in year.iterdir():
            if not folder.is_dir():
                continue
                    
            for file in folder.iterdir():
                if not file.is_file() or not file.suffix == '.nc':
                    continue
                            
                # grabbing date for use in the dict
                re_match = re.search(r'-e(\d{4})(\d{2})(\d{2})', file.name)
                if not re_match:
                    continue
                    
                date = f"{re_match.group(1)}-{re_match.group(2)}-{re_match.group(3)}"
                if date not in paths_for_date:
                    paths_for_date[date] = [file]
                else:
                    paths_for_date[date].append(file)

    for date in paths_for_date:
        print(f"Processing date {date}")

        snr_grid = np.zeros((1800,7200))
        refl_grid = np.zeros((1800,7200))
        count_snr_grid = np.zeros((1800,7200))
        count_refl_grid = np.zeros((1800,7200))

        for file in paths_for_date[date]:
            print(f"- Processing file: {file}")
            snr_grid, refl_grid, count_snr_grid, count_refl_grid = read_file(file, snr_grid, refl_grid, count_snr_grid, count_refl_grid)

        mask_snr = count_snr_grid > 0
        mask_refl = count_refl_grid > 0
    
        snr_grid[mask_snr] = snr_grid[mask_snr] / count_snr_grid[mask_snr]
        refl_grid[mask_refl] = refl_grid[mask_refl] / count_refl_grid[mask_refl]

        snr_grid[~mask_snr] = -9999
        refl_grid[~mask_refl] = -9999

        snr_grid = snr_grid.astype(np.float32)
        refl_grid = refl_grid.astype(np.float32)

        snr_grid.tofile(f"/data01/lpu/CYGNSS/SNR/{date[:4]}/{date}.dat")
        refl_grid.tofile(f"/data01/lpu/CYGNSS/reflectivity/{date[:4]}/{date}.dat")