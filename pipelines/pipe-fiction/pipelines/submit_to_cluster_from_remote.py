import os
import truststore
from utils.auth_session import get_istio_auth_session
from kfp.client import Client
from pipeline import example_pipeline


truststore.inject_into_ssl()


auth_session = get_istio_auth_session(
    url=os.environ["KUBEFLOW_ENDPOINT"],
    username=os.environ["KUBEFLOW_USERNAME"],
    password=os.environ["KUBEFLOW_PASSWORD"],
)
print(os.environ["KUBEFLOW_ENDPOINT"])

namespace = os.environ.get('KUBEFLOW_NAMESPACE', None) or \
            os.environ['KUBEFLOW_USERNAME'].split("@")[0].replace(".", "-")

client = Client(host=f"{os.environ['KUBEFLOW_ENDPOINT']}/pipeline", namespace=namespace,
                cookies=auth_session["session_cookie"], verify_ssl=False)

run = client.create_run_from_pipeline_func(
    example_pipeline,
    enable_caching=False
)
