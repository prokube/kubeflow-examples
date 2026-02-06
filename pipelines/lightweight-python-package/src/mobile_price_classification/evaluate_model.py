import pandas as pd
from joblib import load
from sklearn.metrics import confusion_matrix, classification_report


def evaluate_model(
    val_x_path: str,
    val_y_path: str,
    fitted_scaler_path: str,
    trained_model_path: str,
    classification_report_output_path: str,
) -> list:
    """
    Evaluates the trained SVM model using validation data.
    Returns confusion matrix data and writes classification report to markdown.
    """
    scaler = load(fitted_scaler_path)
    x_val = pd.read_parquet(val_x_path)
    y_val = pd.read_parquet(val_y_path)
    x_val = pd.DataFrame(scaler.transform(x_val), columns=x_val.columns)

    svm_model = load(trained_model_path)
    predictions = svm_model.predict(x_val)

    # Prepare confusion matrix data
    labels = [str(v) for v in sorted(y_val["price_range"].unique())]
    matrix = confusion_matrix(
        y_val["price_range"].values.tolist(), predictions.tolist()
    ).tolist()

    # Write classification report to markdown
    markdown_content = (
        f"```\n{classification_report(y_val['price_range'].values, predictions)}\n```"
    )
    with open(classification_report_output_path, "w") as f:
        f.write(markdown_content)

    return {"labels": labels, "matrix": matrix}
