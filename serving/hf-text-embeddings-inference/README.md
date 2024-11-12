## Create Secret

To securely use an API-Key within your Kubernetes environment, you need to
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
  name: reranking-api-key-secret
  namespace: kubeflow-user-example-com
type: Opaque
data:
  api-key: <base64-encoded-api-key>
```

Apply the Secret to Your Kubernetes Cluster Save the YAML file and apply it to your Kubernetes cluster using the following command:
```sh
kubectl apply -f secret.yaml
```

## nginx config
For this simple example, we're using node ports. Please add these settings to
your nginx config under /etc/nginx/nginx.conf on the host.

```txt
    location /text-embeddings/ {
        proxy_pass http://127.0.0.1:32236;
        proxy_http_version 1.1;
        proxy_set_header Host      35.204.177.255;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        rewrite ^/text-embeddings/(.*)$ /$1 break;
    }

    location /reranking/ {
        proxy_pass http://127.0.0.1:32237;
        proxy_http_version 1.1;
        proxy_set_header Host      35.204.177.255;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        rewrite ^/reranking/(.*)$ /$1 break;
    }
```

## Embeddings

With node port and nginx config

```sh
 curl "https://<you host>/text-embeddings/embed" \
    -k \
    -d '{"inputs":"What is Deep Learning?"}' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer <your token>'
```

## Rerankings

```sh
curl "https://<you host>/reranking/rerank" \
    -k \
    -d '{"query":"What is Deep Learning?", "texts": ["Deep Learning is not...", "Deep learning is..."]}' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer <your token>'
```
