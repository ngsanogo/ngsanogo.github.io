# syntax=docker/dockerfile:1
# ----------------------------
# Stage 1 — Hugo base
# ----------------------------
FROM alpine:3.21 AS hugo

ARG HUGO_VERSION=0.143.1

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

RUN --mount=type=cache,target=/var/cache/apk \
    apk add --no-cache git nodejs npm \
    && pip install --no-cache-dir pre-commit

WORKDIR /site


# ----------------------------
# Stage 2 — Build static site
# ----------------------------
FROM hugo AS build

COPY . .
RUN hugo --minify


# ----------------------------
# Stage 3 — Production (nginx)
# ----------------------------
FROM nginx:1.27-alpine AS prod

LABEL org.opencontainers.image.source="https://github.com/ngsanogo/ngsanogo.github.io" \
      org.opencontainers.image.description="Personal blog - Issa Sanogo" \
      org.opencontainers.image.licenses="MIT"

# Copy custom nginx config with security headers
RUN cat <<'EOF' > /etc/nginx/conf.d/default.conf
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    location / {
        try_files $uri $uri/ /404.html;
    }
}
EOF

COPY --from=build /site/public /usr/share/nginx/html

RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/run

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
