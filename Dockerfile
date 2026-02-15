# ----------------------------
# Stage 1 — Hugo base
# ----------------------------
FROM alpine:3.21 AS hugo

ARG HUGO_VERSION=0.143.1

RUN apk add --no-cache curl \
    && curl -fsSL \
       "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz" \
       | tar xz -C /usr/local/bin hugo \
    && hugo version

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

COPY --from=build /site/public /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
