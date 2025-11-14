FROM python:3.11.5-slim-bookworm

WORKDIR /api

# gcc is required to build hnswlib which is required by chromadb
RUN apt-get update && \
    apt install python3-dev build-essential -y && \
    apt-get install libgeos-dev -y && \
    rm -rf /var/lib/apt/lists/*
COPY ./assets/healthscribe/ ./assets/healthscribe/

ADD Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv sync --system --dev --verbose

COPY autoscribe ./autoscribe

EXPOSE 11000
CMD ["uvicorn", "autoscribe.entrypoints.http:app", "--host", "0.0.0.0", "--port", "11000", "--reload"]
