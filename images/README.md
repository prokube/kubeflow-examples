# Images
This folder contains code and Dockerfiles to create container images used elsewhere.

GitHub Actions publishes development builds to
`europe-west3-docker.pkg.dev/prokube/development`. Release tags matching
`vX.Y.Z` or `vX.Y.Z-rcN` publish every repository image to
`europe-west3-docker.pkg.dev/prokube/releases` with only the unchanged Git tag.
The `GCP_SA_KEY` GitHub secret must have access to both repositories.

Local builds use the development registry:

```sh
make build-all
make push-all TAG=<development-tag>
```
