import pickle
import numpy as np
from tqdm import tqdm
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

SPIRE_BINARIES = '/data01/lpu/SPIRE/reflectivity/2024'
CYGNSS_BINARIES = '/data01/lpu/CYGNSS/reflectivity/2024'
start_date, end_date = '2024-01-25', '2024-06-02'

def grab_data():
    spire_data, cygnss_data = [], []

    for i, file in tqdm(enumerate(Path(SPIRE_BINARIES).iterdir()), desc="Grabbing data"):
        spire_grid = np.fromfile(file.as_posix(), dtype=np.float32)
        spire_grid = spire_grid.reshape((3600, 7200))[900:2700, :]
        spire_data.append(spire_grid)

        path = f"{CYGNSS_BINARIES}/{file.name}"
        cygnss_grid = np.fromfile(path, dtype=np.float32)
        cygnss_grid = cygnss_grid.reshape((1800, 7200))
        cygnss_data.append(cygnss_grid)

    spire_data = np.array(spire_data)
    cygnss_data = np.array(cygnss_data)

    print("SPIRE Shape: ", spire_data.shape)
    print("CYGNSS Shape: ", cygnss_data.shape)

    return spire_data, cygnss_data

if __name__ == "__main__":
    spire_data, cygnss_data = grab_data()

    slope_grid = np.full((1800, 7200), -9999)
    intercept_grid = np.full((1800, 7200), -9999)
    mse_grid = np.full((1800, 7200), -9999)
    rmse_grid = np.full((1800, 7200), -9999)

    for r in tqdm(range(1800), desc="Fitting data"):
        for c in tqdm(range(7200), desc="Fitting data", leave=False):
            spire_pixel = spire_data[:, r, c]
            cygnss_pixel = cygnss_data[:, r, c]

            valid_mask = (spire_pixel != -9999) & (cygnss_pixel != -9999)

            if np.sum(valid_mask) < 2:
                continue

            X = spire_pixel[valid_mask].reshape(-1, 1)
            Y = cygnss_pixel[valid_mask]

            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

            model = LinearRegression().fit(X_train, Y_train)
            slope_grid[r, c] = model.coef_[0]
            intercept_grid[r, c] = model.intercept_

            # getting model MSE and RMSE for test set
            predictions = model.predict(X_test)
            mse_grid[r, c] =  mean_squared_error(Y_test, predictions)
            rmse_grid[r, c] = np.sqrt(mse_grid[r, c])

    with open('/data01/lpu/slope_grid.pkl', 'wb') as f:
        pickle.dump(slope_grid, f)
    with open('/data01/lpu/intercept_grid.pkl', 'wb') as f:
        pickle.dump(intercept_grid, f)
    with open('/data01/lpu/r2_grid.pkl', 'wb') as f:
        pickle.dump(r2_grid, f)
    with open('/data01/lpu/mse_grid.pkl', 'wb') as f:
        pickle.dump(mse_grid, f)
    with open('/data01/lpu/rmse_grid.pkl', 'wb') as f:
        pickle.dump(rmse_grid, f)