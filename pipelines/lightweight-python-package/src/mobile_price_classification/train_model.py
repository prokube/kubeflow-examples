from typing import Dict

import pandas as pd
from sklearn.svm import SVC
from joblib import dump, load


def train_model(
    train_x_path: str,
    train_y_path: str,
    fitted_scaler_path: str,
    hparams: Dict,
    trained_model_output_path: str,
    seed: int = 42,
):
    """
    Trains an SVM classifier using the best hyperparameters from tuning.
    """
    scaler = load(fitted_scaler_path)

    x_train = pd.read_parquet(train_x_path)
    y_train = pd.read_parquet(train_y_path)
    x_train = pd.DataFrame(scaler.transform(x_train), columns=x_train.columns)

    svm_model = SVC(random_state=seed, **hparams)
    svm_model.fit(x_train, y_train["price_range"].values)

    dump(svm_model, trained_model_output_path)
