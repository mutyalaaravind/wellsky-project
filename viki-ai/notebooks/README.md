# Notebooks

## Prerequisites

- Docker

or

- Python 3.11+
- Pipenv

## Running locally

```
make init
make run-local
```

Then navigate to `http://127.0.0.1:8888/treee?token=...` (find URL in logs).

## Running in Docker

```
# Authenticate in Google (credentials will be mounted into Docker container)
gcloud auth application-default login

# Run jupyter notebook server inside Docker
make run
```
