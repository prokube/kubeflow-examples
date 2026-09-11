# Images
This folder contains code and Dockerfiles to create container images used elsewhere.

Manual GitHub Actions builds publish commit and `latest` tags for all six
repository Dockerfiles to `europe-west3-docker.pkg.dev/prokube/development`.
Release tags matching `vX.Y.Z` or `vX.Y.Z-rcN` publish the unchanged tag only to
`europe-west3-docker.pkg.dev/prokube/releases`.

Publishing requires the `GCP_SA_KEY` GitHub secret with access to the target
Google Artifact Registry repository.
