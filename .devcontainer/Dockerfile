FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG HUGO_VERSION=0.143.1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        make \
        nodejs \
        npm \
        pre-commit \
        python3 \
        python3-pip \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
    "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz" \
    | tar xz -C /usr/local/bin hugo

WORKDIR /workspace
