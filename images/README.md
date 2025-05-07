# Images
This folder contains code and dockerfiles to create container images used elsewhere.

To build images either:
1. Push this repository to GitLab CI.
2. Build with GitHub CI. For that, run workflows defined in `.github/workflows`. Those are tailored to be used with GCP artifact registry. Ensure the following GitHub secrets are set:
    ```tx
    GCP_ARTIFACT_REGISTRY_PATH
    GCP_SA_KEY
    ```
