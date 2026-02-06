import pandas as pd
from sklearn.model_selection import train_test_split


def split_data(
    train_df_path: str,
    x_train_output_path: str,
    y_train_output_path: str,
    x_val_output_path: str,
    y_val_output_path: str,
    test_size: float = 0.5,
    seed: int = 42,
):
    """Splits the provided dataset into training and validation sets."""
    data = pd.read_parquet(train_df_path)

    y = data["price_range"].to_frame()
    x_data = data.drop(["price_range"], axis=1)

    x_train, x_val, y_train, y_val = train_test_split(
        x_data, y, test_size=test_size, random_state=seed
    )

    x_train.to_parquet(x_train_output_path)
    y_train.to_parquet(y_train_output_path)
    x_val.to_parquet(x_val_output_path)
    y_val.to_parquet(y_val_output_path)
