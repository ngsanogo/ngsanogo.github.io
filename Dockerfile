# syntax=docker/dockerfile:1
# ----------------------------
# Stage 1 — Hugo base
# ----------------------------
FROM alpine:3.23 AS hugo

ARG HUGO_VERSION=0.157.0

RUN --mount=type=cache,target=/var/cache/apk \
    apk add --no-cache curl ca-certificates \
    && curl -fsSL \
       "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz" \
       | tar xz -C /usr/local/bin hugo \
    && hugo version

WORKDIR /site


# ----------------------------
# Stage 1b — Lint tooling
# ----------------------------
FROM python:3.12-alpine AS lint

ARG PRETTIER_VERSION=3.8.1

RUN --mount=type=cache,target=/var/cache/apk \
    apk add --no-cache bash curl git nodejs npm \
    && pip install --no-cache-dir pre-commit \
    && npm install --global --no-progress "prettier@${PRETTIER_VERSION}"

WORKDIR /site
COPY . .


# ----------------------------
# Stage 2 — Build static site
# ----------------------------
FROM hugo AS build

COPY . .
RUN hugo --minify
