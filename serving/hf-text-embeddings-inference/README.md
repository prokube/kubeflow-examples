## Hugging Face Text Embeddings Inference
Currently, vLLM does not support embedding or reranking models. Therefore, this
example demonstrates how to deploy the Hugging Face Text Embeddings Inference
(TEI) containers.

## Deploy the Helm chart
### Prerequisites
Check the values file. If you want to modify the default values, you can either:
- change the values directly in the `values.yaml` file
- add them to the helm command using `--set` flags, e.g.: `--set apiKey=<your token>`
- use a custom values file in the helm command with `-f <your values file>`.

### Install or update the chart
```sh
helm upgrade --install <release-name> ./serving/hf-text-embeddings-inference \
    --namespace <namespace> --create-namespace
```

## Routing
If you configured external access, we are using NodePorts. Please add the following
settings to your Nginx configuration at `/etc/nginx/nginx.conf` on the host:

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
Test the new config and restart Nginx:
```sh
sudo nginx -t
sudo systemctl restart nginx
```

## Sending Requests with internal access
For internal access (ClusterIP), you can send requests to the models as follows:

### Embeddings request:
```sh
curl --location 'http://<release-name>-text-embeddings-service.<namespace>.svc.cluster.local/v1/embeddings' \
    --header 'Content-Type: application/json' \
    --data '{
        "input": 
        [
            "MLOPs might be important"
        ],
        "model": "intfloat/multilingual-e5-large-instruct"
    }'
```

### Reranking request:
```sh
curl "http://<release-name>-reranking-service.<namespace>.svc.cluster.local/v1/reranking" \
    -d '{
        "query":"What is MLOPs?", 
        "texts": [
            "Deep Learning is not...", 
            "Deep learning is...", 
            "Machine Learning Operation is...", 
            "DevOps seams to be ..."
        ]
    }' \
    -H 'Content-Type: application/json'
```

## Sending Requests with external access
For external access (NodePort and Nginx configuration), you can send requests to the models as follows:

### Embeddings request:
```sh
curl --location '<your host>/v1/embeddings' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer <your token>' \
    --data '{
        "input": 
        [
            "MLOPs might be important"
        ],
        "model": "intfloat/multilingual-e5-large-instruct"
    }'
```

### Reranking request:
```sh
curl "<your host>/v1/reranking" \
    -d '{
        "query":"What is MLOPs?", 
        "texts": [
            "Deep Learning is not...", 
            "Deep learning is...", 
            "Machine Learning Operation is...", 
            "DevOps seems to be ..."
        ]
    }' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer <your token>'
```

## Cleanup
To delete the release, run:
```sh
helm delete <release-name> --namespace <namespace>
```
If you modified the Nginx configuration, please remove the added settings from
`/etc/nginx/nginx.conf` and reload Nginx:
```sh
sudo systemctl restart nginx
```
