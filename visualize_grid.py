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

def visualize_SPIRE():
    with open('/data01/lpu/spire_snr_grid.pkl', 'rb') as f:
        spire_snr_grid = pickle.load(f)
        create_figure(spire_snr_grid, "SPIRE SNR (01/25/2024-06/02/2024)", "SNR (dB)", "figures/spire_snr_map.png", 0, 2, -90, 90)
    with open('/data01/lpu/spire_reflectivity_grid.pkl', 'rb') as f:
        spire_refl_grid = pickle.load(f)
        create_figure(spire_refl_grid, "SPIRE Reflectivity (01/25/2024-06/02/2024)", "Reflectivity (dBZ)", "figures/spire_reflectivity_map.png", 0, 0.015, -90, 90)

def visualize_CYGNSS():
    with open('/data01/lpu/cygnss_snr_grid.pkl', 'rb') as f:
        cygnss_snr_grid = pickle.load(f)
        create_figure(cygnss_snr_grid, "CYGNSS SNR (01/25/2024-06/02/2024)", "SNR (dB)", "figures/cygnss_snr_map.png", 0, 2, -45, 45)
    with open('/data01/lpu/cygnss_reflectivity_grid.pkl', 'rb') as f:
        cygnss_refl_grid = pickle.load(f)
        create_figure(cygnss_refl_grid, "CYGNSS Reflectivity (01/25/2024-06/02/2024)", "Reflectivity (dBZ)", "figures/cygnss_reflectivity_map.png", 0, 0.015, -45, 45)

def visualize_binary_examples():
    with open('/data01/lpu/CYGNSS/reflectivity/2023/2023-02-01.pkl', 'rb') as f:
        cygnss_refl_grid = pickle.load(f)
        create_figure(cygnss_refl_grid, "CYGNSS Reflectivity 02-01-2023", "Reflectivity (dBZ)", "figures/cygnss_refl_binary_map.png",  0, 0.015, -45, 45)
    with open('/data01/lpu/SPIRE/reflectivity/2024/20240125.pkl', 'rb') as f:
        spire_snr_grid = pickle.load(f)
        create_figure(spire_snr_grid, "SPIRE Reflectivity 01-25-2024", "SNR (dB)", "figures/spire_snr_binary_map.png",  0, 2, -90, 90) 

if __name__ == "__main__":
    # i've ran into memory issues with this file, seemingly from caching too much
    # closing the terminal and reopening seems to fix this for mes
    visualize_SPIRE()
    visualize_CYGNSS()    
    # visualize_binary_examples()