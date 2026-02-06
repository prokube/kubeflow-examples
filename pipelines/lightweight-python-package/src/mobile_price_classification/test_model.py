import pandas as pd
from joblib import load
import plotly.express as px


def test_model(
    test_x_path: str,
    trained_model_path: str,
    fitted_scaler_path: str,
    column_x: str,
    column_y: str,
    scatter_plot_output_path: str,
):
    """
    Test a trained SVM model on test data and produce a scatter plot.
    """
    scaler = load(fitted_scaler_path)
    x_test = pd.read_parquet(test_x_path)
    x_test = x_test.drop("id", axis=1)
    x_test = pd.DataFrame(scaler.transform(x_test), columns=x_test.columns)

    svm_model = load(trained_model_path)
    predictions = svm_model.predict(x_test)

    x_test["Predicted Class"] = predictions

    fig = px.scatter(
        x_test,
        x=column_x,
        y=column_y,
        color="Predicted Class",
        color_continuous_scale="Viridis",
        title=f"Scatter plot of {column_x} vs. {column_y} colored by Predicted Class",
        template="plotly_dark",
    )

    fig.write_html(scatter_plot_output_path)
