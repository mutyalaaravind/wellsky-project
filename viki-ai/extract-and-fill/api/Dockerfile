FROM python:3.11.5-slim-bookworm

WORKDIR /api

# gcc is required to build hnswlib which is required by chromadb
RUN apt-get update && \
    apt install python3-dev wget build-essential libgeos-dev -y && \
    rm -rf /var/lib/apt/lists/*

# RUN export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

# RUN wget https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda-repo-debian12-12-3-local_12.3.0-545.23.06-1_amd64.deb
# RUN dpkg -i cuda-repo-debian12-12-3-local_12.3.0-545.23.06-1_amd64.deb
# RUN cp /var/cuda-repo-debian12-12-3-local/cuda-*-keyring.gpg /usr/share/keyrings/
# RUN add-apt-repository contrib
# RUN apt-get update
# RUN apt-get -y install cuda-toolkit-12-3
# RUN apt-get install -y cuda-drivers

ADD Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv sync --system --dev --verbose

COPY extract_and_fill ./extract_and_fill

EXPOSE 11000
CMD ["uvicorn", "extract_and_fill.entrypoints.http1:app", "--host", "0.0.0.0", "--port", "12000", "--reload"]
