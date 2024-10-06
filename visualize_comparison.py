import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pickle

def calculate_statistics(grid1, grid2):
    if grid1.shape != grid2.shape:
        return None

    diff = np.full(grid1.shape, -9999.00)
    mask = ~(grid1 == -9999.00) & ~(grid2 == -9999.00)
    diff[mask] = grid1[mask] - grid2[mask]
    valid_diff = diff[mask]

    bias = np.mean(valid_diff)
    rmsd = np.sqrt(np.mean(valid_diff**2))
    corr_coeff = np.corrcoef(grid1, grid2)[0, 1]

    stats = (bias, rmsd, corr_coeff)
    diff_grid = np.full(grid1.shape, -9999.00)
    diff_grid[mask] = np.abs(grid1[mask] - grid2[mask])

    return diff_grid, stats

# creates a matplotlib figure for a given grid over an Earth map
def create_figure(grid, title, label, file_name, isomin, isomax, latmin, latmax, stats=None):
    fig, ax = plt.subplots(figsize=(12, 8))

    # the Basemap library adds a map of the Earth for easy viewing
    m = Basemap(projection='cyl', llcrnrlat=latmin, urcrnrlat=latmax,
                llcrnrlon=0, urcrnrlon=360, resolution='c', ax=ax)

    # creates a meshgrid from [0, 360] and [latmin, latmax] used to translate argument grid to lon and lat values 
    lon_vals = np.linspace(0, 360, grid.shape[1])
    lat_vals = np.linspace(latmin, latmax, grid.shape[0])
    lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)

    # remove values that are equal to -9999
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

    # If statistics are provided, add them as annotations
    if stats:
        bias, rmsd, corr = stats
        textstr = '\n'.join((
            f"Bias: {bias:.4f}",
            f"RMSD: {rmsd:.4f}",
            f"Correlation: {corr:.4f}"
        ))
        # place the text box in the lower-left corner of the plot
        props = dict(boxstyle='round', facecolor='white', alpha=0.7)
        ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='bottom', bbox=props)

    plt.savefig(file_name, dpi=300, bbox_inches='tight')
    plt.close()

def visualize_SPIRE_vs_CYGNSS():
    with open('/data01/lpu/spire_snr_grid.pkl', 'rb') as f:
        spire_snr_grid = pickle.load(f)
    with open('/data01/lpu/spire_reflectivity_grid.pkl', 'rb') as f:
        spire_refl_grid = pickle.load(f)
    with open('/data01/lpu/cygnss_snr_grid.pkl', 'rb') as f:
        cygnss_snr_grid = pickle.load(f)
    with open('/data01/lpu/cygnss_reflectivity_grid.pkl', 'rb') as f:
        cygnss_refl_grid = pickle.load(f)

    spire_refl_grid = spire_refl_grid[900:2700, :]
    refl_grid, stats = calculate_statistics(spire_refl_grid, cygnss_refl_grid)
    create_figure(refl_grid, "SPIRE vs CYGNSS Reflectivity", "Abs. Diff. in Reflectivity (dBZ)", "figures/comp_reflectivity_map.png", 0, 0.015, -45, 45, stats) 

    spire_snr_grid = spire_snr_grid[900:2700, :]
    snr_grid, stats = calculate_statistics(spire_snr_grid, cygnss_snr_grid)
    create_figure(snr_grid, "SPIRE vs CYGNSS SNR", "Abs. Diff. in SNR (dB)", "figures/comp_snr_map.png", 0, 10, -45, 45, stats) 


if __name__ == "__main__":
    # i've ran into memory issues with this file, seemingly from caching too much
    # closing the terminal and reopening seems to fix this for mes
    visualize_SPIRE_vs_CYGNSS()