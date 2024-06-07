FROM python:slim-bullseye

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/rancher/cli/releases/download/v2.8.4/rancher-linux-amd64-v2.8.4.tar.gz && \
    tar -xvf rancher-linux-amd64-v2.8.4.tar.gz && \
    mv rancher-v2.8.4/rancher /usr/local/bin/ && \
    rm -rf rancher-linux-amd64-v2.8.4.tar.gz rancher-v2.8.4

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

RUN pip install k8ctl==0.0.10