```sh
SERVICE_HOST=35.204.177.255
MODEL_NAME=qwen-model-name
INVERENCE_SERVICE_NAME=qwen-inf-serv
NAMESPACE=kubeflow-user-example-com
X_API_KEY=XXXXX

curl -v https://$SERVICE_HOST/serving/${NAMESPACE}/${INVERENCE_SERVICE_NAME}/openai/v1/chat/completions \
-H "content-type: application/json" \
-H "Host: ${SERVICE_HOST}" \
-H "x-api-key: ${X_API_KEY}" \
-k \
-d "{\"model\":\"${MODEL_NAME}\",\"messages\":[{\"role\":\"system\",\"content\":\"You are an assistant.\"},{\"role\":\"user\",\"content\":\"What is MLOPs?\"}],\"max_tokens\":200,\"stream\":true}"
```
