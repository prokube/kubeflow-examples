from typing import List

import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from joblib import load


def tune_hyperparams(
    train_x_path: str,
    train_y_path: str,
    fitted_scaler_path: str,
    C: List = None,
    kernel: List = None,
    gamma: List = None,
    decision_function_shape: List[str] = None,
    seed: int = 42,
) -> dict:
    """
    Performs hyperparameter tuning using GridSearchCV for an SVM classifier.
    Returns the best hyperparameters found.
    """
    if C is None:
        C = [1, 0.1, 0.25, 0.5, 2, 0.75]
    if kernel is None:
        kernel = ["linear", "rbf"]
    if gamma is None:
        gamma = ["auto", 0.01, 0.001, 0.0001, 1]
    if decision_function_shape is None:
        decision_function_shape = ["ovo", "ovr"]

    scaler = load(fitted_scaler_path)

    x_train = pd.read_parquet(train_x_path)
    y_train = pd.read_parquet(train_y_path)
    x_train = pd.DataFrame(scaler.transform(x_train), columns=x_train.columns)

    svm = SVC(random_state=seed)

    grid_svm = GridSearchCV(
        estimator=svm,
        cv=5,
        param_grid=dict(
            kernel=kernel,
            C=C,
            gamma=gamma,
            decision_function_shape=decision_function_shape,
        ),
    )

    grid_svm.fit(x_train, y_train["price_range"].values)

    print("Best score: ", grid_svm.best_score_)

    return grid_svm.best_params_
