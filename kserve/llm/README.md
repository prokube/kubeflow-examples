# Serving a simple language model from HuggingFace with KServe

This example shows how to build a custom model from HuggingFace for serving with KServe without using a predefined ServingRuntime custom resource.

More information:
* [KServe](https://kserve.github.io/website/master/modelserving/v1beta1/custom/custom_model/) 
* [HuggingFace LLM interface](https://huggingface.co/docs/transformers/llm_tutorial)

## General steps
1. Define `custom_model.py` file with the expected model and methods.
2. Define `requirements.txt` with all necessary dependencies.
3. To load models from HuggingFace, you need your code to know HuggingFace read token:
```env
HUGGINGFACE_API_TOKEN=hf_...
```
You can either configure a `.env` file with this secret (local run) or specify a secret with it (in a cluster).

## Run locally
1. Create and activate a venv:
```sh
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # won't work with python 3.13
```
2. Start KServe server with the defined model:
```sh
python custom_model.py
```
3. Test that model serving is working: 
```sh
curl -H "Content-Type: application/json" localhost:8080/v1/models/llm-example:predict -d '{"text": "Hello"}'
```

## Run in k8s cluster
To run the model in a cluster, we need to pack it into a Docker container and create an InferenceService in a cluster. The workflow proposed by KServe uses `buildpacks` and requires a Procfile with text `web: python custom_model.py`. That does not work too well with ARM processors, so here is an alternative Docker workflow:
1. Define a `Dockerfile` (see example).
2. Build and push the image:
```bash
# build and push image from python code (does not work for M1)
# pack build --builder=heroku/builder:24 ${DOCKER_USER}/kserve-lm:v1 -e --platform linux/amd64
docker build -t ${DOCKER_USER}/kserve-lm:v1 --platform linux/amd64 .
docker push ${DOCKER_USER}/kserve-lm:v1
```
3. To test if the container works correctly locally (AMD64 processors only): 
```bash
docker run -e PORT=8080 -p 8080:8080 ${DOCKER_USER}/kserve-lm:v1
curl -H "Content-Type: application/json" localhost:8080/v1/models/llm-example:predict -d '{"text": "Hello"}'
```
---
To run the model in a prokube cluster:
1. Define a secret with HuggingFace API token and an InferenceService with a built image (see `sample_inference_service.yaml`).
2. Apply the manifest (with necessary secret information):
```sh
export HUGGINGFACE_API_TOKEN=$(echo -n "${YOUR_API_TOKEN}" | base64)
envsubst < sample_inference_service.yaml | kubectl apply -n ${YOUR_NAMESPACE} -f -
```
3. Wait for corresponding InferenceService to start and run:
```sh
curl -v -k \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${YOUR_API_KEY}" \
  "https://${INGRESS_HOST}/serving/$YOUR_NAMESPACE}/custom-lm/v1/models/llm-example:predict" \
  -d '{"text": "Hello"}'
```
