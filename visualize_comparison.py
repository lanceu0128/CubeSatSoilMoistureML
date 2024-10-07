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

def create_figure(grid, title, label, file_name, isomin, isomax, lonmin, lonmax, latmin, latmax, stats=None):
    fig, ax = plt.subplots(figsize=(12, 8))

    m = Basemap(projection='cyl', llcrnrlat=latmin, urcrnrlat=latmax,
                llcrnrlon=lonmin, urcrnrlon=lonmax, resolution='c', ax=ax)

    lon_vals = np.linspace(0, 360, grid.shape[1])
    lat_vals = np.linspace(-45, 45, grid.shape[0])
    lon_grid, lat_grid = np.meshgrid(lon_vals, lat_vals)

    masked_grid = np.ma.masked_where(grid == -9999, grid)

    cs = m.pcolormesh(lon_grid, lat_grid, masked_grid, shading='auto', 
                      cmap='viridis', vmin=isomin, vmax=isomax)

    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.5)

    m.drawparallels(np.arange(-90, 91, 20), labels=[1, 0, 0, 0])  
    m.drawmeridians(np.arange(0, 361, 20), labels=[0, 0, 0, 1])  

    cbar = m.colorbar(cs, location='right', pad="5%")
    cbar.set_label(label)

    ax.set_title(title)

    if stats:
        bias, rmsd, corr = stats
        textstr = '\n'.join((
            f"Bias: {bias:.4f}",
            f"RMSD: {rmsd:.4f}",
            f"Correlation: {corr:.4f}"
        ))
        props = dict(boxstyle='round', facecolor='white', alpha=0.7)
        ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='bottom', bbox=props)

    plt.savefig(file_name, dpi=300, bbox_inches='tight')
    plt.close()

def visualize_SPIRE_vs_CYGNSS():
    with open('/data01/lpu/spire_reflectivity_grid.pkl', 'rb') as f:
        spire_refl_grid = pickle.load(f)
    with open('/data01/lpu/cygnss_reflectivity_grid.pkl', 'rb') as f:
        cygnss_refl_grid = pickle.load(f)

    spire_refl_grid = spire_refl_grid[900:2700, :]
    refl_grid, stats = calculate_statistics(spire_refl_grid, cygnss_refl_grid)
    create_figure(refl_grid, "SPIRE vs CYGNSS Reflectivity (012024-062024)", "Abs. Diff. in Reflectivity (dBZ)", "figures/comp_reflectivity_map.png", 0, 0.06, 0, 360, -45, 45, stats) 

    spire_snr_grid = spire_snr_grid[900:2700, :]
    snr_grid, stats = calculate_statistics(spire_snr_grid, cygnss_snr_grid)
    create_figure(snr_grid, "SPIRE vs CYGNSS SNR (012024-062024)", "Abs. Diff. in SNR (dB)", "figures/comp_snr_map.png", 0, 16, 0, 360, -45, 45, stats) 

def visualize_SPIRE_vs_CGYNSS_area():
    with open('/data01/lpu/spire_reflectivity_grid.pkl', 'rb') as f:
        spire_refl_grid = pickle.load(f)
    with open('/data01/lpu/cygnss_reflectivity_grid.pkl', 'rb') as f:
        cygnss_refl_grid = pickle.load(f)

    spire_refl_grid = spire_refl_grid[900:2700, :]
    refl_grid, _ = calculate_statistics(spire_refl_grid, cygnss_refl_grid)
    
    create_figure(refl_grid, "SPIRE vs CYGNSS Reflectivity, Australia (01-06/2024)", "Abs. Diff. in Reflectivity (dBZ)", "figures/comp_reflectivity_australia_map.png", 0, 0.06, 100, 160, -45, -10) 
    create_figure(refl_grid, "SPIRE vs CYGNSS Reflectivity, North/Central America (01-06/2024)", "Abs. Diff. in Reflectivity (dBZ)", "figures/comp_reflectivity_america_map.png", 0, 0.06, 220, 300, 10, 45)

if __name__ == "__main__":
    # visualize_SPIRE_vs_CYGNSS()
    visualize_SPIRE_vs_CGYNSS_area()