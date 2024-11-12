# nginx config
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

# Embeddings

With node port and nginx config

```sh
 curl "https://35.204.177.255/text-embeddings/embed" \
    -k \
    -d '{"inputs":"What is Deep Learning?"}' \
    -H 'Content-Type: application/json'
```

# Rerankings

```sh
curl "https://35.204.177.255/reranking/rerank" \
    -k \
    -d '{"query":"What is Deep Learning?", "texts": ["Deep Learning is not...", "Deep learning is..."]}' \
    -H 'Content-Type: application/json'
```
