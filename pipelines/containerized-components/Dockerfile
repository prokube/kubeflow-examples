FROM python:3.9-slim

WORKDIR /app

# Copy and install the package
COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .
