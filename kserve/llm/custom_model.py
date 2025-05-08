# https://kserve.github.io/website/master/modelserving/v1beta1/custom/custom_model/
# https://huggingface.co/docs/transformers/llm_tutorial
import os
from typing import Dict, Union

import torch
from dotenv import load_dotenv
from kserve import InferRequest, Model, ModelServer
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "distilgpt2"


class SampleLM(Model):
    def __init__(self, name: str):
        super().__init__(name)
        load_dotenv()
        self.name = name
        self.load()

    def load(self) -> bool:
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME, token=hf_token, torch_dtype=torch.float16
            )
            print("Model loaded successfully")
            self.ready = True
        except Exception as e:
            print(f"Error loading model: {e}")
            self.ready = False
        return self.ready

    def predict(
        self, payload: Union[Dict, InferRequest], headers: Dict[str, str] = {}
    ) -> str:
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, padding_side="left", token=hf_token, torch_dtype=torch.float16
        )
        tokenizer.pad_token = tokenizer.eos_token
        text = payload["text"]
        model_inputs = tokenizer([text], return_tensors="pt")
        generated_ids = self.model.generate(
            **model_inputs, max_new_tokens=30, do_sample=True
        )
        output = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        return output


if __name__ == "__main__":
    model = SampleLM("llm-example")
    ModelServer().start([model])
