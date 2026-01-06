#!/bin/sh
set -e

# Create .streamlit config directory if needed
mkdir -p ~/.streamlit

# Build streamlit command with optional baseUrlPath
if [ -n "$NB_PREFIX" ]; then
    echo "[server]" > ~/.streamlit/config.toml
    echo "headless = true" >> ~/.streamlit/config.toml
    echo "port = 8888" >> ~/.streamlit/config.toml
    echo 'address = "0.0.0.0"' >> ~/.streamlit/config.toml
    echo "enableCORS = false" >> ~/.streamlit/config.toml
    echo "enableXsrfProtection = false" >> ~/.streamlit/config.toml
    echo "baseUrlPath = \"$NB_PREFIX\"" >> ~/.streamlit/config.toml
    echo "" >> ~/.streamlit/config.toml
    echo "[browser]" >> ~/.streamlit/config.toml
    echo "gatherUsageStats = false" >> ~/.streamlit/config.toml
    
    exec streamlit run /app/streamlit_app/app.py
else
    exec streamlit run /app/streamlit_app/app.py \
        --server.port 8888 \
        --server.address 0.0.0.0
fi
