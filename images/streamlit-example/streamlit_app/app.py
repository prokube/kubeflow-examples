import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Kubeflow Streamlit Demo", layout="centered")

st.title("Kubeflow Streamlit Demo")

# Controls
value = st.slider("Choose a value", min_value=0, max_value=100, value=50)
text = st.text_input("Describe this run", "Initial run")

# Create a small data table
dates = pd.date_range("2025-01-01", periods=10)
data = pd.DataFrame({"value": (np.sin(np.linspace(0, 3.14, 10)) * value / 100) + np.random.rand(10) * 0.1}, index=dates)

st.subheader("Generated metrics")
st.line_chart(data)

st.write("You entered:", text)

st.caption("This app can be run inside Kubeflow notebooks or deployed via Kubernetes manifests behind Istio.")
