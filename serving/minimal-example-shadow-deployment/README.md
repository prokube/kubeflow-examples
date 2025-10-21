# Minimal shadow deployment

When you'd like to try a new model with production data without risking anything, a
shadow deployment might be a good fit. 

This example contains everything you need to deploy your own custom transformer/predictor
and the corresponding resources to mirror the traffic. 


## Structure

To be able to use the shadow deployment, the `InferenceService` needs to store the
request and response of each request. To do this, the **minimal-transformer** example
contains a PredictionDBHandler that stores the request and response body with some
metadata in a Postgres database.

The **minimal-predictor** is a small example custom predictor that multiplies the
input values with some factor that is defined in an environment variable. This is
especially useful for testing purposes since you don't have to build a new image if
you'd like to change the predictor output. 

We used CrunchyLabs postgres-operator to deploy a postgres cluster in the namespace
where you have deployed both inference services. If you have the operator deployed in
your cluster, you can use the **postsgres-cluster.yml** to deploy your database.

[!Warning]
Make sure to create all required tables before you deploy the inference service. The
transformer does **not** create them. 

Once two inference services are deployed and they persist each request in some way
`Istio` can be used to mirror the traffic. In each virtual service you have to insert
the correct inference uri. 

```
uri: /serving/prokube-demo-profile/double-minimal-custom-inference/
```

Then use the `kustomization.yaml` to deploy both VirtualServices

## Development and debugging

The predictor and transformer are two independent `uv` managed projects. Both are
structured in a similar way; therefore, they can be treated similar.

[!Note]
The debugging configuration is varying slightly in both projects. Please consult the
README for further information.


Install all dependencies and activate the virtual environment. This project is using uv to do that:

```bash
uv sync
source ./venv/bin/activate
``` 

Run each python file according to the corresponding README.md and use the following
command to test the inference. 

First define the `DOMAIN`,`PROFILE_NAME` and `X_API_KEY` environment
variables. 

```bash
curl -L -X POST \
  "$DOMAIN_NAME/serving/$PROFILE_NAME/mirrored-inference/v1/models/model:predict" \
  -H "Content-Type: application/json" \
  -H "Test-Header" \-H "x-api-key: ${X_API_KEY}" \
  -d '{"values": ["3.3", "62.3","324"]}'
```
