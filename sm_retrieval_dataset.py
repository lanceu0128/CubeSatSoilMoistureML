import torch, glob, os
from torch.utils.data import Dataset, DataLoader
import numpy as np

class SoilMoistureRetrievalDataset(Dataset):
    def __init__(self, cygnss_dir, years, smap_paths=None):
        self.cygnss_paths = []

        for year in years:
            year_files = glob.glob(os.path.join(cygnss_dir, f"{year}", "*.dat"))
            self.cygnss_paths.extend(year_files)
        
    def __len__(self):
        return len(self.cygnss_paths)

    def __getitem__(self, idx):
        cygnss_path = self.cygnss_paths[idx]
        cygnss_data = np.fromfile(cygnss_path, dtype=np.float32).reshape(1800, 7200)

        cygnss_data = torch.tensor(cygnss_data)

        return cygnss_data

base_dir = "/data01/lpu/CYGNSS/reflectivity"
years = ["2018"] 

dataset = SoilMoistureRetrievalDataset(base_dir, years)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True, num_workers=4)

for batch in dataloader:
    pass