FROM python:3.11.5-slim-bookworm

WORKDIR /api

ARG LOCAL
# gcc is required to build hnswlib which is required by chromadb
RUN apt-get update && \
    apt install python3-dev build-essential -y && \
    apt-get install libgeos-dev -y && \
    rm -rf /var/lib/apt/lists/*

ADD Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv sync --system --dev --verbose

# "Thank" you, Google!
# This is required for files downloaded with "nltk.download()" to work in Cloud Run
# https://chanind.github.io/2021/09/27/cloud-run-home-env-change.html
#RUN if [[ -z "$LOCAL" ]]; then echo 'running in local'  else ENV HOME=/home ;fi

ENV HOME=/home

RUN mkdir ~/nltk_data && \
    mkdir ~/nltk_data/chunkers && \
    mkdir ~/nltk_data/corpora && \
    mkdir ~/nltk_data/taggers && \
    mkdir ~/nltk_data/tokenizers && \
    python -c "import nltk; nltk.download(['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words'])" && \
    python -m spacy download en_core_web_md

COPY paperglass ./paperglass

COPY newrelic.ini newrelic.ini
ENV NEW_RELIC_CONFIG_FILE=newrelic.ini

EXPOSE 15000
CMD ["uvicorn", "paperglass.entrypoints.http1:app", "--host", "0.0.0.0", "--port", "15000", "--reload"]
