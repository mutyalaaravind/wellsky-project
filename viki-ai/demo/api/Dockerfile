FROM python:3.11.5-slim-bookworm

WORKDIR /api

# gcc is required to build hnswlib which is required by chromadb
RUN apt-get update && \
    apt install python3-dev build-essential -y && \
    rm -rf /var/lib/apt/lists/*

ADD Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv sync --system --dev --verbose

COPY main ./main

EXPOSE 13000
CMD ["uvicorn", "main.entrypoints.http:app", "--host", "0.0.0.0", "--port", "13000", "--reload"]
