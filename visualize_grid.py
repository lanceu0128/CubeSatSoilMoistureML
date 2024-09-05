import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pickle

def create_figure(grid, title, label, file_name, isomin, isomax):
    fig, ax = plt.subplots(figsize=(12, 8))
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90,
                llcrnrlon=-180, urcrnrlon=180, resolution='c', ax=ax)

    lon_vals = np.linspace(-180, 180, grid.shape[1])
    lat_vals = np.linspace(-90, 90, grid.shape[0])
    lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)

    cs = m.pcolormesh(lon_grid, lat_grid, grid, shading='auto', 
                    cmap='viridis', vmin=isomin, vmax=isomax)

    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)

    cbar = m.colorbar(cs, location='right', pad="5%")
    cbar.set_label(label)

    ax.set_title(title)

    plt.savefig(file_name, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    with open('/data01/lpu/snr_grid.pkl', 'rb') as f:
        snr_grid = pickle.load(f)
    with open('/data01/lpu/reflectivity_grid.pkl', 'rb') as f:
        reflectivity_grid = pickle.load(f)

    print(f"SNR Min: {np.min(snr_grid)}, Max: {np.max(snr_grid)}")
    print(f"Reflectivity Min: {np.min(reflectivity_grid)}, Max: {np.max(reflectivity_grid)}")

    create_figure(snr_grid, "SNR 06-08-2024", "SNR (dB)", "snr_map.png", 0.00001, 10)
    create_figure(reflectivity_grid, "Reflectivity 06-08-2024", "Reflectivity (dBZ)", "reflectivity_map.png", 0.00001, 0.01)