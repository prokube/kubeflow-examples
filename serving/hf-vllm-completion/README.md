# Using KServe to Deploy LLMs
KServe [supports](https://kserve.github.io/website/latest/modelserving/v1beta1/llm/huggingface/) Hugging Face serving runtime, which has 2 backend options: vLLM and huggingface. 

## Deploying with vLLM backend on a GPU cluster
In this example, we demonstrate how to deploy a model with vLLM as the backend. This requires a GPU available.

On prokube, you can simply deploy the inference service manifest located in
this directory:

```sh
kubectl apply -f inference-service.yaml -n <your-namespace>
```

Once the endpoint is displayed as `READY` in the Kubeflow UI, you can send
requests to the model. Example qwen model endpoint will support OpenAI Completion API with extra vLLM features:

```sh
SERVICE_HOST=<your host>
NAMESPACE=<your namespace>
X_API_KEY=<your key>
MODEL_NAME=qwen
INFERENCE_SERVICE_NAME=qwen-inf-serv

curl -v https://$SERVICE_HOST/serving/${NAMESPACE}/${INFERENCE_SERVICE_NAME}/openai/v1/chat/completions \
```

You can also get the model endpoint route (`https://$SERVICE_HOST/serving/${NAMESPACE}/${INFERENCE_SERVICE_NAME}`) from the Endpoints UI in Kubeflow.

## Deploying with huggingface backend on a CPU cluster
If a GPU is not available, Huggingface Backend will be used by default (KServe currently (v0.15.0) does not support vLLM backend for CPU clusters). If your cluster is CPU only, you can use the following example as a starting point:

```sh
kubectl apply -f inference-service-cpu.yaml -n <your-namespace>
```

Once the endpoint is displayed as `READY` in the Kubeflow UI, you can send 
requests to the model as follows:

```sh
SERVICE_HOST=<your host>
NAMESPACE=<your namespace>
X_API_KEY=<your key>
MODEL_NAME=distilbert
INFERENCE_SERVICE_NAME=distilbert-inf-serv

curl -v https://$SERVICE_HOST/serving/${NAMESPACE}/${INFERENCE_SERVICE_NAME}/v1/models/${MODEL_NAME}:predict \
     -H "content-type: application/json" \
     -H "Host: ${SERVICE_HOST}" \
     -H "x-api-key: ${X_API_KEY}" \
     -d '{
     "instances": ["vLLM is wonderful!"]
   }
```

## Deploying a model from a huggingface gated repo
This will require a secret with huggingface API token configured:
```
kubectl create secret generic hf-secret --from-literal=HF_TOKEN=<YOUR TOKEN> -n <namespace>
```
Then simply add this to your `spec.predictor.model` in the InferenceService yaml:
```yaml
      env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-secret
              key: HF_TOKEN
              optional: false
```
