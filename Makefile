.PHONY: dev build test prod clean lint help

help:
	@echo "Available commands:"
	@echo "  make dev    - Start dev server with hot reload (port 1313)"
	@echo "  make build  - Build the static site"
	@echo "  make test   - Build and validate output"
	@echo "  make prod   - Run production server (nginx, port 8080)"
	@echo "  make clean  - Remove generated files"
	@echo "  make lint   - Run formatters and linters via pre-commit"

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
	@command -v pre-commit >/dev/null 2>&1 || { \
		echo "❌ Error: pre-commit is not installed"; \
		echo ""; \
		echo "Install it with:"; \
		echo "  brew install pre-commit  # macOS"; \
		echo "  pip install pre-commit   # or with pip"; \
		echo ""; \
		echo "Then run: pre-commit install"; \
		exit 1; \
	}
	@pre-commit run --all-files
