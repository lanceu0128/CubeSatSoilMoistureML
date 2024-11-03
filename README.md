# CubeSatSoilMoistureML

This project's aim is to use ML to obtain soil moisture retrievals through data from other satellites.

## Weekly Reports
Summaries of weekly progress on this project from my end are [here](https://docs.google.com/presentation/d/1B_XuNAdR7wOspA3WuINxxRgFHerD8ueCrNhVuMWLw2A/edit#slide=id.g3115a5e8b0c_0_7).

## Reading Daily Binaries

These files store numpy arrays containing 2D grids of daily readings of either Reflectivity or SNR by the CYGNSS or SPIRE satellites. These grids are generated in 5KM spatial resolution globally. 

CYGNSS covers latitudes [-45, 45] where as SPIRE covers latitudes [-90, 90]. Both cover a full range of longitude [-180, 180].

Specs for each set of readings: 
- CYGNSS
    - Reflectivity
        - Data Format: numpy.float32
        - Array Size: 1800 x 7200
        - File Size: 51.84 MB
        - File Type: .dat
    - SNR
        - Data Format: numpy.float32
        - Array Size: 1800 x 7200
        - File Size: 51.84 MB
        - File Type: .dat
- SPIRE
    - Reflectivity
        - Data Format: numpy.float32
        - Array Size: 3600 x 7200
        - File Size: 103.68 MB
        - File Type: .dat
    - SNR
        - Data Format: numpy.float32
        - Array Size: 3600 x 7200
        - File Size: 103.68 MB
        - File Type: .dat

Reading the files as NumPy arrays is very easy:
```py
import numpy as np
import pickle

with open('/data01/lpu/CYGNSS/reflectivity/2023/2023-02-01.pkl', 'rb') as f:
    cygnss_refl_grid = pickle.load(f)
```

See visualize_grid.py for more examples of the data being used and visualized over a Basemap.