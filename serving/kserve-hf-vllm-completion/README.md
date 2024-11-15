# Using KServe to Deploy LLMs
kserve supports two LLM runtimes: Hugging Face Transformers and vLLM. In this
example, we demonstrate how to deploy a model with vLLM as the backend.

On prokube, you can simply deploy the inference service manifest located in
this directory:

```sh
kubectl apply -f inference-service.yaml
```

Once the endpoint is displayed as `READY` in the Kubeflow UI, you can send
requests to the model as follows:

```sh
SERVICE_HOST=<your host>
MODEL_NAME=qwen-model-name
INVERENCE_SERVICE_NAME=qwen-inf-serv
NAMESPACE=kubeflow-user-example-com
X_API_KEY=XXXXX

curl -v https://$SERVICE_HOST/serving/${NAMESPACE}/${INVERENCE_SERVICE_NAME}/openai/v1/chat/completions \
-H "content-type: application/json" \
-H "Host: ${SERVICE_HOST}" \
-H "x-api-key: ${X_API_KEY}" \
-d "{\"model\":\"${MODEL_NAME}\",\"messages\":[{\"role\":\"system\",\"content\":\"You are an assistant.\"},{\"role\":\"user\",\"content\":\"What is MLOPs?\"}],\"max_tokens\":200,\"stream\":true}"
```
