.PHONY: dev build test prod clean lint setup help

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PRECOMMIT := $(VENV)/bin/pre-commit

help:
	@echo "Available commands:"
	@echo "  make setup  - Create venv and install dev dependencies"
	@echo "  make dev    - Start dev server with hot reload (port 1313)"
	@echo "  make build  - Build the static site"
	@echo "  make test   - Build and validate output"
	@echo "  make prod   - Run production server (nginx, port 8080)"
	@echo "  make clean  - Remove generated files"
	@echo "  make lint   - Run formatters and linters via pre-commit"

setup:
	@echo "🔧 Setting up development environment..."
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@$(PRECOMMIT) install
	@echo "✅ Setup complete! Pre-commit hooks installed."

dev:
	@echo "🌐 Starting dev server..."
	@docker compose --profile dev up --build

build:
	@echo "🔨 Building site..."
	@docker compose --profile build run --rm build

test:
	@echo "🧪 Running tests..."
	@docker compose --profile test run --rm test

prod:
	@echo "🚀 Starting production server..."
	@docker compose --profile prod up --build -d

clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf public/ resources/ .hugo_build.lock
	@echo "✅ Clean complete"

lint:
	@echo "🔍 Running linters..."
	@if [ ! -f "$(PRECOMMIT)" ]; then \
		echo "❌ Error: pre-commit is not installed in venv"; \
		echo ""; \
		echo "Run: make setup"; \
		exit 1; \
	fi
	@$(PRECOMMIT) run --all-files
