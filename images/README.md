# Images
This folder contains code and Dockerfiles to create container images used elsewhere.

GitHub Actions builds all six repository Dockerfiles. Pull requests are build-only;
main and manual builds publish commit and `latest` tags to
`europe-west3-docker.pkg.dev/prokube/development`. Release tags matching `vX.Y.Z`
or `vX.Y.Z-rcN` publish the unchanged tag only to
`europe-west3-docker.pkg.dev/prokube/releases`.

Publishing requires the `GCP_SA_KEY` GitHub secret with access to the target
Google Artifact Registry repository.
