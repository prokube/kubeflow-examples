
## Exp1:
With port forwarding from the `http-qwen-1-5b` to you local machine and no
extra params:
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


## Exp2:
With nodeport and nginx routing and no guided choice:
```sh
curl https://35.204.177.255/qwen-1-5b/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "guided_choice": ["good", "bad"],
        "messages": [
            {"role": "user", "content": "Classify this sentiment: vLLM is wonderful!"}
        ]
    }' \
    -k
```
