# Minimal custom Kserve Predictor

This directory contains an example of a KServe custom predictor.
We use a very simple example here solely to demonstrate the
workflow.

A KServe transformer can be developed in the same way,
in that case only a) the pre- and postprocess methods of the KServe Model
class need to be overridden and b) a predictor must already exist.

## Development and debugging

First, install the dependencies, we're using `uv` to do that:
```sh
uv sync
```
 
Start the server locally, like so (from this directory):
 
```sh
source .venv/bin/activate
python main.py
```
 
See if it works:
```sh
export MODEL_NAME=capitalizer

curl -X POST http://localhost:8080/v1/models/$MODEL_NAME:predict \
  -H "Content-Type: application/json" \
  -d '{"instances": ["prokube", "works"]}'
```
In order to debug your code, you could for example put a `breakpoint()` in line 20 of the `main.py` file.
If you now stop the server, start it again (by running `python
main.py`) and send a query, you will be placed in an ipdb debugging session
in the terminal where you started the server.

## Deploy as KServe inference service
We'll need a container images to run the kserve inference service on the cluster.
Feel free to build the image using the tools you are used to.
However, if you like to build it inside a prokube notebook, you can do it like
so:
1. Launch the pk-podman-shell
```sh
pk-launch-podman-shell
```
2. Navigate to the directory where the Dockerfile lives
3. Build the image using `podman build` or `docker build` which is an alias to
   podman. E.g. like so:
   ```sh
   docker build  --platform=linux/amd64 -t <your-registry/your-imagename:your-tag> .
   ```
4. If you want to push the image to a private registry, you'll need to log in
   first: `docker login <your-registry> -u <your-username>`. You'll be prompted for your
password
5. Once the image is pushed to the registry, you can exit the pk-podman shell with
   Control+D or `exit`.
 
As soon as we have the image, in a registry and the secret to pull it in the
cluster, we can deploy the inference service. Don't forget to modify the
`image` field in the manifest first and also other values if needed.

```sh
```sh
kubectl create -f ./inference-service.yaml -n YOUR-NAMESPACE
```
 
 
Wait and check the UI for the status. And see if its working:
```sh
export MODEL_NAME=capitalizer
export X_API_KEY=<Ask your prokube admin for the x-api key>
curl -X POST \
  "<put the internal url from the kserve ui here>/v1/models/$MODEL_NAME:predict" \
  -H "Content-Type: application/json" \
  -k \
  -H "x-api-key: ${X_API_KEY}" \
  -d '{"instances": ["prokube", "works"]}'
```

If you don't know your API key, reach out to your admin, he'll know what to do.

