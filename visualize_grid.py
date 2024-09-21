import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pickle

# creates a matplotlib figure for a given grid over an Earth map
def create_figure(grid, title, label, file_name, isomin, isomax):
    fig, ax = plt.subplots(figsize=(12, 8))

    # the Basemap library adds a map of the Earth for easy viewing
    m = Basemap(projection='cyl', llcrnrlat=-45, urcrnrlat=45,
                llcrnrlon=0, urcrnrlon=360, resolution='c', ax=ax)

    # creates a meshgrid from [0, 360] and [-90, 90] used to translate argument grid to lon and lat values 
    lon_vals = np.linspace(0, 360, grid.shape[1])
    lat_vals = np.linspace(-45, 45, grid.shape[0])
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
    # with open('/data01/lpu/spire_snr_grid.pkl', 'rb') as f:
    #     spire_snr_grid = pickle.load(f)
    # with open('/data01/lpu/spire_reflectivity_grid.pkl', 'rb') as f:
    #     spire_reflectivity_grid = pickle.load(f)

    # CYGNSS DATA
    # with open('/data01/lpu/cygnss_snr_grid.pkl', 'rb') as f:
    #     cygnss_snr_grid = pickle.load(f)
    # with open('/data01/lpu/cygnss_reflectivity_grid.pkl', 'rb') as f:
    #     cygnss_refl_grid = pickle.load(f)
    with open('/data01/lpu/cygnss_count_snr_grid.pkl', 'rb') as f:
        cygnss_count_snr_grid = pickle.load(f)
    with open('/data01/lpu/cygnss_count_reflectivity_grid.pkl', 'rb') as f:
        cygnss_count_refl_grid = pickle.load(f)

    print(f"Size of Grid: {7200 * 1800}")
    print(f"# of Values where SNR and Refl Count are the same: {np.count_nonzero((cygnss_count_refl_grid == cygnss_count_snr_grid) == True)}")
    print(f"# of Values where SNR and Refl Count are different: {np.count_nonzero((cygnss_count_refl_grid == cygnss_count_snr_grid) == False)}")

    # create_figure(spire_snr_grid, "SPIRE SNR 04-2024", "SNR (dB)", "spire_snr_map.png", 0, 10)
    # create_figure(spire_reflectivity_grid, "SPIRE Reflectivity 04-2024", "Reflectivity (dBZ)", "spire_reflectivity_map.png", -20, 20)
    # create_figure(cygnss_snr_grid, "CYGNSS SNR 04-2024", "SNR (dB)", "cygnss_snr_map.png", 0, 10)
    # create_figure(cygnss_refl_grid, "CYGNSS Reflectivity 04-2024", "Reflectivity (dBZ)", "cygnss_reflectivity_map.png", 0, 0.014)
    create_figure(cygnss_count_snr_grid, "CYGNSS SNR Count 04-2024", "Count", "cygnss_count_snr_map.png", 0, 35)
    create_figure(cygnss_count_refl_grid, "CYGNSS Reflectivity Count 04-2024", "Count", "cygnss_count_reflectivity_map.png", 0, 35)
    