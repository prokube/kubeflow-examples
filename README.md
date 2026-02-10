# kubeflow-examples
Kubeflow examples - Notebooks, Pipelines, Models, Model tuning and more

## Brief description
```py
.
├── .github          # workflows to build images
├── data             # data for some of the examples
├── hparam-tuning    # katib example
├── images           # images for some of the examples
├── mlflow           # mlflow examples (simple jupyter notebook with mlflow and kfp + mlflow example)
├── notebooks        # dask example and an advanced jupyter notebook example
├── pipelines        # kubeflow pipelines examples
├── rstudio          # R-Studio examples
├── serving          # KServe examples
```

## Note about storage
Storage on k8s is a complex topic and deep dive is outside of scope of this repository. There are two types of
storage you might encounter here - block and object storage.

### Block storage
Is the usual type of storage a k8s pod might mount to persist data. An example in the context of this repo are 
Kubeflow Notebook volumes.

### Object storage
Object storage is any S3-like type of storage. Kubeflow Pipelines use object storage 
extensively to store intermediate and final task/pipeline artifacts. Furthermore, KServe can be configured
to serve models directly from object storage.
Kubeflow (if deployed via [manifests](https://github.com/kubeflow/manifests)) comes with [MinIO](https://min.io/) 
built in. Due to MinIO license change the bundled version is quite old, but still functional. Alternatively, 
admins can configure Kubeflow Pipelines to use other instances of object storage (e.g. self-served MinIO, AWS S3, 
GCS, etc.). Relevant for end users it to know that many S3 libraries use environmental variables for their 
configuration. 
Those are usually: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `S3_ENDPOINT`. They are likely already
available in your environment. You can also ask your admin about them or reach out to us -> *prokube* comes 
pre-configured with integrated storage.

## Contributing
All code contributions should go via pull requests. Make sure your code is clearly documented and that it adheres
to established standards (e.g. PEP). 

### Jupyter notebooks
Since this repo contains Jupyter notebooks we use [nbstripout](https://github.com/kynan/nbstripout) as 
[pre-commit](https://pre-commit.com/) hook so all notebooks are stripped of cell outputs. Set it up locally for 
yourself with:
```shell
pip install --upgrade nbstripout
pip install pre-commit 
pre-commit install
```
This should enable the hooks.  
Use `pre-commit run --all-files` to run the hooks.
