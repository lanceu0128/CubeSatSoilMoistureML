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
    with open('/data01/lpu/snr_grid.pkl', 'rb') as f:
        snr_grid = pickle.load(f)
    with open('/data01/lpu/reflectivity_grid.pkl', 'rb') as f:
        reflectivity_grid = pickle.load(f)

    create_bin_figure(snr_grid, "Distribution of Values in SNR 202404 Grid", "snr_bins.png", -30, 30, 5)
    create_bin_figure(reflectivity_grid, "Distribution of Values in Reflectivity 202404 Grid", "reflectivity_bins.png", 0, 10, 1, True)