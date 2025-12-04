---
authors:
  - Issa Sanogo
categories:
  - Application
  - Infrastructure
date: "2025-12-02"
lastmod: "2025-12-02"
description: "Docker explained for data engineers: What it is, why you need it, and how to use it for reproducible data pipelines."
tags:
  - docker
  - containerization
  - infrastructure
  - reproducibility
title: "Docker: How to Run Your Data Pipeline Anywhere"
draft: false
weight: 5
toc: true
---

## What is Docker?

Docker puts your entire application (code, dependencies, configuration, everything) into a box that runs the same on any machine.

Your local laptop. Your colleague's laptop. Production server. Cloud. Everywhere.

That's it. That's Docker.

## The Problem It Solves

You write a Python data pipeline locally. Works perfectly.

You send it to your colleague. Doesn't work.

Why? Different Python version. Different library version. Different operating system. Different everything.

You upload to production. Breaks again.

This happens constantly without Docker.

With Docker: You package everything once. It works everywhere.

## How Docker Works

**Docker Image**: A blueprint. Includes your code, Python version 3.11, PostgreSQL client library, everything.

**Docker Container**: A running instance. Like starting a computer from the image blueprint.

Start the container. Your pipeline runs. Stop the container. Gone. No trace.

Start it again. Same thing happens. Predictable.

## Real Example: Data Pipeline

You have a Python script that:

- Connects to PostgreSQL
- Extracts customer data
- Cleans it
- Loads into warehouse

Locally, you need:

- Python 3.11
- PostgreSQL client
- Libraries: pandas, sqlalchemy, python-dotenv

Without Docker: You hope your colleague has the same versions. Usually they don't.

With Docker: You specify exact versions in a file. Docker builds an image with those exact versions. Colleague runs the same image. Works identically.

## Docker Components

**Dockerfile**: Instructions to build an image.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pipeline.py .

CMD ["python", "pipeline.py"]
```

**Image**: Result of building the Dockerfile.

```bash
docker build -t my-pipeline:1.0 .
```

**Container**: Running instance of the image.

```bash
docker run my-pipeline:1.0
```

**Registry**: Storage for images (Docker Hub, company registry).

```bash
docker push my-pipeline:1.0
docker pull my-pipeline:1.0
```

## Why Data Engineers Need Docker

**Reproducibility**: Exact same environment. Every time.

**No "works on my machine" problems**: If it works in Docker, it works everywhere.

**Easy distribution**: Send an image, not instructions. No setup required.

**Production matching**: Your local Docker environment can match production exactly.

**Isolation**: Your pipeline doesn't mess with other software on the machine.

**Scalability**: Run 100 containers. Each one is identical. All process data the same way.

## Simple Docker Example

Say you have this Python script:

```python
import pandas as pd
from sqlalchemy import create_engine

# Connect to database
engine = create_engine('postgresql://user:pass@localhost:5432/mydb')

# Extract data
df = pd.read_sql('SELECT * FROM orders', engine)

# Transform
df['total'] = df['quantity'] * df['price']

# Load
df.to_sql('orders_processed', engine, if_exists='append')

print("Pipeline completed")
```

To run it without Docker:

```bash
# Hope Python 3.11 is installed
# Hope pandas is installed
# Hope PostgreSQL is installed
# Run it
python pipeline.py
```

Fragile. Breaks.

To run it with Docker:

**Step 1: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pipeline.py .

CMD ["python", "pipeline.py"]
```

**Step 2: Create requirements.txt**

```
pandas==2.1.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
```

**Step 3: Build image**

```bash
docker build -t my-pipeline:1.0 .
```

**Step 4: Run container**

```bash
docker run my-pipeline:1.0
```

Done. Same environment everywhere. Reproducible.

## Real-World Usage: ETL Pipeline

You're running a daily ETL:

```bash
# Run every day at 2 AM
# Docker container starts
docker run my-etl-pipeline:2.0

# Pipeline runs
# Extracts from Salesforce
# Transforms data
# Loads into warehouse
# Container finishes
# Container stops

# No leftover processes
# No dependency conflicts
# No "why isn't this working" debugging
```

Compare to running Python directly:

```bash
# Run Python script
python run_etl.py

# Hope all dependencies are installed
# Hope no versions conflict with other projects
# Hope the database connection works
# Hope the script doesn't crash partway
# If it does, manually restart
# Leaves processes running
# Conflicts with other work on same machine
```

Docker is cleaner. Safer. Reproducible.

## Docker for Local Development

You want to test against PostgreSQL locally.

Without Docker:

```bash
# Install PostgreSQL
# Configure it
# Start the service
# Create a database
# Load test data
# 30 minutes of setup
```

With Docker:

```bash
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  postgres:15

# PostgreSQL is running
# Takes 10 seconds
```

When you're done:

```bash
docker stop postgres
docker rm postgres
```

No leftover software. No configuration. Clean.

## Common Docker Commands

```bash
# Build an image
docker build -t image-name:tag .

# Run a container
docker run image-name:tag

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop container-id

# Remove a container
docker rm container-id

# View container logs
docker logs container-id

# Execute command in running container
docker exec container-id command

# Remove an image
docker rmi image-name:tag
```

## Why Docker Matters for Data Engineering

**Pipeline reliability**: Same code, same results, every run.

**Easy collaboration**: "Run this image" instead of "install these 5 things and hope it works."

**Production confidence**: Test locally in Docker. Deploy the same image. Works identically.

**Scaling**: Need to run 10 parallel pipelines? Run 10 containers.

**Monitoring**: Docker makes it easy to see what's running, stop it, restart it, collect logs.

## Docker Compose for Complex Setups

You need PostgreSQL, Redis, and your Python app running together.

Instead of three separate commands:

```yaml
version: "3"
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
  redis:
    image: redis:7
  pipeline:
    build: .
    depends_on:
      - postgres
      - redis
```

Run one command:

```bash
docker compose up
```

All three services start. They can talk to each other. Done.

## Real Example: Running Locally

You have a data pipeline that needs PostgreSQL, Python, and some libraries.

**Without Docker**:

- Install PostgreSQL (15 minutes)
- Install Python 3.11 (10 minutes)
- Create virtual environment (5 minutes)
- Install libraries (5 minutes)
- Configure database (10 minutes)
- Total: ~45 minutes before you can run anything

Someone else tries to run it. Different PostgreSQL version. Different Python version. Doesn't work. 2 hours debugging.

**With Docker**:

- Create Dockerfile (10 minutes, done once)
- Create docker-compose.yml (10 minutes, done once)
- Run: `docker compose up` (10 seconds)
- Colleague runs: `docker compose up` (10 seconds)
- Identical result

Time saved: Hours. Frustration eliminated: Massive.

## Docker Best Practices

**Use specific versions**

```dockerfile
# Good
FROM python:3.11.0-slim

# Bad
FROM python:latest
```

**Keep images small**

```dockerfile
# Good - minimal image
FROM python:3.11-slim

# Bad - bloated
FROM python:3.11
```

**One main process per container**

```dockerfile
# Good - one job
CMD ["python", "pipeline.py"]

# Bad - trying to do too much
CMD ["service postgres start && python pipeline.py"]
```

**Use .dockerignore**

```
.git
__pycache__
*.pyc
.env
```

## The Learning Curve

Docker has a learning curve, but not steep:

**Day 1**: Understand what Docker is, run an existing image.

**Day 2**: Create your first Dockerfile, build an image.

**Day 3**: Run your data pipeline in Docker, get it working.

**Week 1**: Comfortable with Docker. Using it daily.

Worth the time investment.

## Bottom Line

Docker is how modern data pipelines run.

Without Docker: "It works on my machine."

With Docker: It works everywhere.

Every data engineer should know Docker. Not optional. Essential.

Learn it now. Use it daily. Your pipelines will be more reliable, reproducible, and shareable.
