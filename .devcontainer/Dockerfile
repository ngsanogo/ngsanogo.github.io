FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG HUGO_VERSION=0.156.0
ARG NODE_MAJOR=20
ARG PRETTIER_VERSION=3.8.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        git \
        make \
        pre-commit \
        python3 \
        python3-pip \
        wget \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
       | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" \
       > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install --global --no-progress "prettier@${PRETTIER_VERSION}" \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
    "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz" \
    | tar xz -C /usr/local/bin hugo

WORKDIR /workspace
