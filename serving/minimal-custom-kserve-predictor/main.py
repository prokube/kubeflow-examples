import os
from typing import Dict
from kserve import Model, ModelServer

class StringCapitalizerPredictor(Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = True
    
    def predict(self, request: Dict, headers: Dict[str, str] = None) -> Dict:
        """Taks a string capitalizes it and returns it"""
        
        
        if "instances" not in request or not request["instances"]:
            return {"predictions": ["No input provided"]}

        results = []
        for instance in request["instances"]:
            # breakpoint()
            results.append(instance.upper())

        return {"results": results}

if __name__ == "__main__":
    model_name = os.environ.get("MODEL_NAME", "capitalizer")
    model = StringCapitalizerPredictor(model_name)
    ModelServer().start([model])

