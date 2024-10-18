import numpy as np
import matplotlib.pyplot as plt
import pickle

def create_bin_figure(grid, title, file_name, min_val, max_val, bin_size, log_scale=False):
    # filter out default data
    filtered_grid = grid[grid != -9999]

    # create bins of 5
    offset = bin_size / 2
    min_val = np.floor(min_val / bin_size) * bin_size
    max_val = np.ceil(max_val / bin_size) * bin_size
    bins = np.arange(min_val-offset, max_val+offset, bin_size)

    # create a histogram from the bins 
    counts, edges = np.histogram(filtered_grid, bins=bins)

    # plotting stuff
    plt.bar(edges[:-1], counts, width=bin_size, edgecolor="black", align="edge")
    plt.xlabel('Value Range')
    plt.ylabel('Count')
    plt.title(title)
    
    if log_scale:
        plt.yscale('log')

    plt.savefig(file_name, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    with open('/data01/lpu/slope_grid.pkl', 'rb') as f:
        slope_grid = pickle.load(f)
    with open('/data01/lpu/mse_grid.pkl', 'rb') as f:
        mse_grid = pickle.load(f)

    print(np.max(slope_grid[slope_grid != -9999]))
    print(np.max(mse_grid[mse_grid != -9999]))

    create_bin_figure(slope_grid, "Distribution of Values in LR Slope", "figures/regression/slope_bins.png", 0, 1000000, 1000, True)
    create_bin_figure(mse_grid, "Distribution of Values in LR MSE", "figures/regression/mse_bins.png", 0, 1000000, 1000, True)