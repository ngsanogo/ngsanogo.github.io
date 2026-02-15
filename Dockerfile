# Static site generator — Python 3.11 stdlib only.
# Light image, non-root user, minimal layers.
# https://github.com/ngsanogo/ngsanogo.github.io

FROM python:3.11-slim

# Single layer for system user
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy project (see .dockerignore to exclude public/, .git, cache)
COPY --chown=app:app . .

USER app

EXPOSE 8000

# Default: build then serve (override in docker-compose for test/build)
CMD ["sh", "-c", "python3 src/build.py && python3 src/dev.py"]
