FROM python:3.11.5-slim-bookworm

WORKDIR /notebooks

# gcc is required to build hnswlib which is required by chromadb
RUN apt-get update && \
    apt install python3-dev build-essential -y && \
    rm -rf /var/lib/apt/lists/*

ADD Pipfile Pipfile.lock .
RUN pip install pipenv
RUN pipenv sync --system --dev --verbose

COPY src ./src

EXPOSE 8888
CMD ["jupyter", "notebook", "--allow-root", "--ip", "0.0.0.0", "--port", "8888"]
