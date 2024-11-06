
```sh
SERVICE_HOST=35.204.177.255
MODEL_NAME=mamba-130m-hf-model-name
INVERENCE_SERVICE_NAME=mamba-130m-hf-inf-serv
NAMESPACE=kubeflow-user-example-com
X_API_KEY=XXXXX

curl -v https://$SERVICE_HOST/serving/${NAMESPACE}/${INVERENCE_SERVICE_NAME}/openai/v1/chat/completions \
-H "content-type: application/json" -H "Host: ${SERVICE_HOST}" \
-H "x-api-key: ${X_API_KEY}" \
-d "{\"model\":\"${MODEL_NAME}\",\"messages\":[{\"role\":\"system\",\"content\":\"You are an assistant.\"},{\"role\":\"user\",\"content\":\"Who are\"}],\"max_tokens\":200,\"stream\":true}" \
-k
```
