# Using KServe to Deploy LLMs
KServe [supports](https://kserve.github.io/website/latest/modelserving/v1beta1/llm/huggingface/) Hugging Face serving runtime, which has 2 backend options: Hugging Face and vLLM. In this example, we demonstrate how to deploy a model with vLLM as the backend.

On prokube, you can simply deploy the inference service manifest located in
this directory:

```sh
kubectl apply -f inference-service.yaml -n <your-namespace>
```

Once the endpoint is displayed as `READY` in the Kubeflow UI, you can send 
requests to the model as follows:

```sh
SERVICE_HOST=<your host>
NAMESPACE=<your namespace>
X_API_KEY=<your key>
MODEL_NAME=qwen
INFERENCE_SERVICE_NAME=qwen-inf-serv

curl -v https://$SERVICE_HOST/serving/${NAMESPACE}/${INFERENCE_SERVICE_NAME}/openai/v1/chat/completions \
-H "content-type: application/json" \
-H "Host: ${SERVICE_HOST}" \
-H "x-api-key: ${X_API_KEY}" \
-d "{\"model\":\"${MODEL_NAME}\",\"messages\":[{\"role\":\"system\",\"content\":\"You are an assistant.\"},{\"role\":\"user\",\"content\":\"What is MLOPs?\"}],\"max_tokens\":200,\"stream\":true}"
```

You can also get the model endpoint route (`https://$SERVICE_HOST/serving/${NAMESPACE}/${INFERENCE_SERVICE_NAME}`) from the Endpoints UI in Kubeflow.
