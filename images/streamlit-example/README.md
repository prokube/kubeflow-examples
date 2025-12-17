# Kubeflow Streamlit Example

A Streamlit demo app that runs both as a Kubeflow notebook and as a standalone Kubernetes deployment with Istio. The app includes interactive widgets (slider, text input) and data visualization.

## Converting Your Existing Streamlit App

To convert your existing Streamlit app to work with Kubeflow, you need to address **URL path prefixing** and **port configuration**. The key challenge is that Kubeflow serves apps under path prefixes (like `/streamlit/` or `/notebook/<namespace>/<name>/`) rather than at the root URL. This template solves this with an **entrypoint script** (`entrypoint.sh`) that dynamically configures Streamlit's `baseUrlPath` based on the `NB_PREFIX` environment variable. For your app: (1) Copy the `entrypoint.sh` script and reference it in your Dockerfile's CMD, (2) Ensure your app runs on **port 8888** (Kubeflow notebook standard), (3) Set `STREAMLIT_SERVER_ENABLE_CORS=false` and `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false` for Istio compatibility, (4) In your Kubernetes manifests, set the `NB_PREFIX` env var to match your VirtualService prefix (e.g., `/streamlit`), and (5) Create an Istio `AuthorizationPolicy` to allow traffic from the ingress gateway. The entrypoint script handles all the Streamlit configuration automatically, so your application code remains unchanged.

## Building the Docker Image

**For Mac (especially Apple Silicon)**, specify platform for Linux AMD64:
```bash
docker build --platform linux/amd64 -t <registry>/streamlit-demo:latest .
docker push <registry>/streamlit-demo:latest
```

**For Linux AMD64 hosts**:
```bash
docker build -t <registry>/streamlit-demo:latest .
docker push <registry>/streamlit-demo:latest
```

Update the image reference in the manifests if using a different registry.

## Deployment Options

### Option 1: Kubeflow Notebook (Port 8888)
Deploy as a notebook interface on the standard Kubeflow notebook port:

```bash
kubectl apply -f k8s/notebook-deployment.yaml
```

- **Port**: 8888 (Kubeflow notebook standard)
- **Access**: `http://<kubeflow-host>/notebook/<namespace>/streamlit-notebook/`
- **Features**: Includes persistent storage, StatefulSet deployment
- **Note**: Update namespace in manifest to match your Kubeflow user namespace

### Option 2: Standalone Deployment (Port 8888)
Deploy as a regular service:

```bash
kubectl apply -f k8s/streamlit-manifests.yaml
```

- **Port**: 8888 (same as notebook for consistency)
- **Access**: `http://streamlit.kubeflow.example.com`
- **Features**: Lightweight Deployment, no persistent storage
- **Note**: Update hostname in VirtualService to match your DNS

## Running Locally in a Kubeflow Notebook
1. Open a Notebook server in your Kubeflow namespace
2. Clone this repository
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run Streamlit on the notebook port:
   ```bash
   streamlit run streamlit_app/app.py --server.port 8888 --server.address 0.0.0.0
   ```
5. Access via the notebook's proxy URL

## Running as Custom Notebook Image
When using the Docker image directly as a custom notebook image in Kubeflow:

1. The image automatically detects the `NB_PREFIX` environment variable
2. Streamlit configures itself with the correct base URL path
3. Access the app at: `http://<kubeflow-host>/notebook/<namespace>/<notebook-name>/`

**Troubleshooting**:
- Try accessing with a trailing slash: `/notebook/<namespace>/<notebook-name>/`
- Check browser console for errors (websocket connection issues)
- Verify the `NB_PREFIX` env var is set correctly in the notebook pod
- Check Istio/networking policies allow traffic to port 8888

## Notes
- The Dockerfile installs requirements globally inside the image. For production, pin every dependency if the app grows.
- Istio sidecar injection is enabled via `sidecar.istio.io/inject: "true"` on the Pod template. Adjust or disable it if deploying outside Kubeflow.
- If you want to expose the app through another VirtualService or Gateway, copy the Istio section and adjust the hosts/gateway selectors accordingly.
- The entrypoint script (`entrypoint.sh`) dynamically configures Streamlit based on whether `NB_PREFIX` is set
