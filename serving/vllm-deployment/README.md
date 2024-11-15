# vLLM Deployment
This example demonstrates how to deploy a vLLM model without using KServe.
Although KServe uses vLLM as the LLM runtime when the model is supported by
vLLM, currently, KServe does not support the extra parameters specific to vLLM.


## Deploy the Model
The deployment can be initiated from this directory as follows:
```sh
kubectl apply -f http-qwen-1-5b
```

## Routing
To keep this example simple, we are using a NodePort to make the model
accessible from outside. The following change needs to be made in the Nginx
configuration of the host:
```txt
    location /v1/chat/completions {
        proxy_pass http://127.0.0.1:32235/v1/chat/completions;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
```


## Sending Requests:
### Exp1:
Using port forwarding from the `http-qwen-1-5b` ClusterIP service to your local
machine with no extra parameters:
```sh
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Wie wird das Wetter morgen?"}
        ],
        "stream":"true"
    }'
```


### Exp2:
Using NodePort and Nginx routing with no guided choice:
```sh
 curl https://<your host>/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "guided_choice": ["positive", "negative"],
        "messages": [
            {"role": "user", "content": "Classify this sentiment: vLLM is wonderful!"}
        ]
    }' \
```
