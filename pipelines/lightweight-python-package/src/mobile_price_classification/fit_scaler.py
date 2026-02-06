import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from joblib import dump


def fit_scaler(train_x_path: str, fitted_scaler_output_path: str):
    """Fits a MinMaxScaler on the provided training data and saves it."""
    x_train = pd.read_parquet(train_x_path)

    scaler = MinMaxScaler()
    scaler.fit(x_train)

    dump(scaler, fitted_scaler_output_path)
