import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pickle

# creates a matplotlib figure for a given grid over an Earth map
def create_figure(grid, title, label, file_name, isomin, isomax, latmin, latmax):
    fig, ax = plt.subplots(figsize=(12, 8))

    # the Basemap library adds a map of the Earth for easy viewing
    m = Basemap(projection='cyl', llcrnrlat=latmin, urcrnrlat=latmax,
                llcrnrlon=0, urcrnrlon=360, resolution='c', ax=ax)

    # creates a meshgrid from [0, 360] and [-90, 90] used to translate argument grid to lon and lat values 
    lon_vals = np.linspace(0, 360, grid.shape[1])
    lat_vals = np.linspace(latmin, latmax, grid.shape[0])
    lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)

    # remove values that are equal to -9999 (the default value in make_grid.py)
    masked_grid = np.ma.masked_where(grid == -9999, grid)

    cs = m.pcolormesh(lon_grid, lat_grid, masked_grid, shading='auto', 
                    cmap='viridis', vmin=isomin, vmax=isomax)

    # customization stuff
    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)

    m.drawparallels(np.arange(-90, 91, 20), labels=[1, 0, 0, 0])  # Latitude lines
    m.drawmeridians(np.arange(0, 361, 20), labels=[0, 0, 0, 1])   # Longitude lines

    cbar = m.colorbar(cs, location='right', pad="5%")
    cbar.set_label(label)

    ax.set_title(title)

    plt.savefig(file_name, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # SPIRE DATA
    with open('/data01/lpu/spire_snr_grid.pkl', 'rb') as f:
        spire_snr_grid = pickle.load(f)
        # create_figure(spire_snr_grid, "SPIRE SNR 04-2024", "SNR (dB)", "figures/spire_snr_map.png", 0, 2, -90, 90)
    with open('/data01/lpu/spire_reflectivity_grid.pkl', 'rb') as f:
        spire_refl_grid = pickle.load(f)
        # create_figure(spire_refl_grid, "SPIRE Reflectivity 04-2024", "Reflectivity (dBZ)", "figures/spire_reflectivity_map.png", 0, 0.015, -90, 90)

    # CYGNSS DATA
    with open('/data01/lpu/cygnss_snr_grid.pkl', 'rb') as f:
        cygnss_snr_grid = pickle.load(f)
        # create_figure(cygnss_snr_grid, "CYGNSS SNR 04-2024", "SNR (dB)", "figures/cygnss_snr_map.png", 0, 2, -45, 45)
    with open('/data01/lpu/cygnss_reflectivity_grid.pkl', 'rb') as f:
        cygnss_refl_grid = pickle.load(f)
        # create_figure(cygnss_refl_grid, "CYGNSS Reflectivity 04-2024", "Reflectivity (dBZ)", "figures/cygnss_reflectivity_map.png", 0, 0.015, -45, 45)

    # SPIRE VS CYGNSS SNR DATA COMPARISON
    comp_snr_grid = np.full((1800, 7200), -9999)
    clipped_spire_snr_grid = spire_snr_grid[900:2700, :]
    known_snr_mask = ~(clipped_spire_snr_grid == -9999) & ~(cygnss_snr_grid == -9999)
    comp_snr_grid[known_snr_mask] = np.abs(clipped_spire_snr_grid[known_snr_mask] - cygnss_snr_grid[known_snr_mask])
    create_figure(comp_snr_grid, "SPIRE vs CYGNSS SNR 04-2024", "Abs. Diff. in SNR (dB)", "figures/comp_snr_map.png", 0, 10, -45, 45) 

    # SPIRE VS CYGNSS REFLECTIVITY DATA COMPARISON
    comp_refl_grid = np.full((1800, 7200), -9999)
    clipped_spire_refl_grid = spire_refl_grid[900:2700, :]
    known_refl_mask = ~(clipped_spire_refl_grid == -9999) & ~(cygnss_refl_grid == -9999)
    comp_refl_grid[known_refl_mask] = np.abs(clipped_spire_refl_grid[known_refl_mask] - cygnss_refl_grid[known_refl_mask])
    create_figure(comp_refl_grid, "SPIRE vs CYGNSS Reflectivity 04-2024", "Abs. Diff. in Reflectivity (dBZ)", "figures/comp_reflectivity_map.png", 0, 0.075, -45, 45) 