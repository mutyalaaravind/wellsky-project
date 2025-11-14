# Frontends

This directory contains microfrontends.

Each microfrontend is a separate directory with its own `Dockerfile.dev` for running in a development environment.

During deployment, they are copied to a CDN and run container-less.

To run all of them:

```sh
# Copy .npmrc from root directory to each microfrontend's directory.
# This is needed to install private packages.
# You only need to do this once.
make configure

# Log in to GCP with the service account that can generate signed URLs.
gcloud auth application-default login --impersonate-service-account=viki-ai-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com

# Run all microfrontends.
make run
```

Now go to <http://127.0.0.1:16001> to see MedWidget.
