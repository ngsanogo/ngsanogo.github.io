# ----------------------------
# Stage 1 — Builder
# ----------------------------
FROM python:3.11-slim AS builder

# Security: non-root user
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy source
COPY --chown=app:app . .

# Ensure workspace directory itself remains writable after copy operations
RUN chown -R app:app /app

USER app

# Build static site
RUN python3 src/build.py


# ----------------------------
# Stage 2 — Runtime (minimal)
# ----------------------------
FROM python:3.11-slim AS runtime

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy only what is needed to serve
COPY --from=builder --chown=app:app /app/public ./public
COPY --from=builder --chown=app:app /app/src ./src

USER app

EXPOSE 8000

CMD ["python3", "src/dev.py"]
