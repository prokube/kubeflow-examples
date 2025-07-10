import argparse
import base64
import io
import logging
import os
from datetime import datetime, timezone
from typing import Dict

import kserve
from kserve import Model, ModelServer, model_server
from kserve.model import PredictorProtocol

from PredictionDBHandler import PredictionDBHandler

logging.basicConfig(level=kserve.constants.KSERVE_LOGLEVEL)

REQUEST_ID = "request_id"

logger = logging.getLogger(__name__)


class PersistTransformer(kserve.Model):
    def __init__(
        self,
        name: str,
        predictor_host: str,
        db_url: str,
    ):
        super().__init__(name)
        self.predictor_host = predictor_host
        self.postges_db_handler = PredictionDBHandler(db_url)

    def preprocess(self, inputs: Dict, headers: Dict[str, str]):
        if REQUEST_ID not in headers:
            logger.error(
                "Request: Header %s not found! Continue without storeing...", REQUEST_ID
            )
        else:
            self.postges_db_handler.queue_request(
                headers[REQUEST_ID],
                datetime.now(timezone.utc),
                self.predictor_host,
                inputs,
            )
        return inputs

    def postprocess(self, inputs: Dict, headers: Dict[str, str]) -> Dict:
        if REQUEST_ID not in headers:
            logger.error(
                "Response: Header %s not found! Continue without storeing...",
                REQUEST_ID,
            )
        else:
            self.postges_db_handler.queue_response(headers[REQUEST_ID], inputs)
        return inputs


parser = argparse.ArgumentParser(parents=[model_server.parser])
parser.add_argument(
    "--predictor_host", help="The URL for the model predict function", required=True
)
parser.add_argument("--db_url", help="Postgres URI", required=True)

parser.add_argument("--model_name", help="The name that the model is served under.")

args, _ = parser.parse_known_args()

if __name__ == "__main__":
    model = PersistTransformer(
        args.model_name, predictor_host=args.predictor_host, db_url=args.db_url
    )
    ModelServer().start(models=[model])
