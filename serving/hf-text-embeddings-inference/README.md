## Hugging Face Text Embeddings Inference
Currently, vLLM does not support embedding or reranking models. Therefore, this
example demonstrates how to deploy the Hugging Face Text Embeddings Inference
(TEI) containers.

## Create a Secret

To use an API-Key within your Kubernetes environment, you need to
create a secret that holds the encoded value of the key. Here's how you can do
it:

1. Encode the API-Key Before creating the secret, you should base64-encode your
   API-Key to ensure it is safely stored in Kubernetes. Use the following
   command to encode your API-Key:
```sh
echo -n 'your_api_key_here' | base64
```
2. Create the Secret YAML File Next, create a YAML file to define the
   Kubernetes Secret. Ensure you replace <base64-encoded-api-key> with the
   actual base64 string you obtained from the previous step. Here’s how you can
   set up the YAML file:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: hf-text-embeddings-api-key-secret
type: Opaque
data:
  api-key: <base64-encoded-api-key>
```

Apply the Secret to the namespace where the deployment will be running and to
the monitoring namespace, like so:
```sh
kubectl apply -f secret.yaml -n kubeflow-user-example-com
kubectl apply -f secret.yaml -n monitoring 
```


## Deploy the Model
Initiate the deployment from this directory with the following commands:
```sh
kubectl apply -f embeddings.yaml
kubectl apply -f reranking.yaml
```



## Routing
For this simple example, we are using NodePorts. Please add the following
settings to your Nginx configuration under `/etc/nginx/nginx.conf` on the host:

```txt

        location /v1/embeddings {
            proxy_pass http://127.0.0.1:32236/v1/embeddings;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /v1/reranking {
            proxy_pass http://127.0.0.1:32237/rerank;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
```

## Sending Requests
With NodePort and Nginx configuration, you can send requests to the models as follows:

### Embeddings request:
```sh
curl --location '<your host>/v1/embeddings' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer <your token>' \
--data '{
    "input": 
    [
        "MLOPs is might be important"
    ],
    "model": "intfloat/multilingual-e5-large-instruct"
}'
```
## Request reranking:
```sh
curl "<your host>/v1/reranking" \
    -d '{"query":"What is MLOPs?", "texts": ["Deep Learning is not...", "Deep learning is...", "Machine Learning Operation is...", "DevOps seams to be ..."]}' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer <your token>'
```
