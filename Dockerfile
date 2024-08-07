FROM python:slim-bullseye

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    vim \
    wget \
    bash-completion \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/rancher/cli/releases/download/v2.8.4/rancher-linux-amd64-v2.8.4.tar.gz && \
    tar -xvf rancher-linux-amd64-v2.8.4.tar.gz && \
    mv rancher-v2.8.4/rancher /usr/local/bin/ && \
    rm -rf rancher-linux-amd64-v2.8.4.tar.gz rancher-v2.8.4

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

RUN echo 'source /usr/share/bash-completion/bash_completion' >> ~/.bashrc && \
    echo "alias k=kubectl" >> ~/.bashrc && \
    echo 'source <(kubectl completion bash)' >> ~/.bashrc && \
    echo 'complete -o default -F __start_kubectl k' >> ~/.bashrc

RUN pip install k8ctl