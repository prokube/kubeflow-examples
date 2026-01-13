FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir streamlit==1.52.1 pandas==2.2.3 numpy==1.26.4

# Create app directory
WORKDIR /app
COPY streamlit_app /app/streamlit_app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose Streamlit port (8888 for Kubeflow notebook compatibility)
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Entrypoint handles NB_PREFIX for Kubeflow notebook base URL routing
CMD ["/app/entrypoint.sh"]
