import os
import pandas as pd


def read_data(
    minio_train_data_path: str,
    minio_test_data_path: str,
    train_output_path: str,
    test_output_path: str,
):
    """Reads training and test data from MinIO and writes to parquet files."""
    storage_options = {
        "key": os.environ.get("AWS_ACCESS_KEY_ID"),
        "secret": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "client_kwargs": {"endpoint_url": "http://minio.minio"},
    }

    df_train = pd.read_csv(minio_train_data_path, storage_options=storage_options)
    df_test = pd.read_csv(minio_test_data_path, storage_options=storage_options)

    df_train.to_parquet(train_output_path)
    df_test.to_parquet(test_output_path)
