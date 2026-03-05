.PHONY: setup hooks dev build test test-versions ci prod clean lint stop help

help:
	@echo "Available commands:"
	@echo "  make setup  - Build Docker images (first-time setup)"
	@echo "  make hooks  - Configure repository git hooks"
	@echo "  make dev    - Start dev server with hot reload (port 1313)"
	@echo "  make build  - Build the static site"
	@echo "  make test   - Build and validate output"
	@echo "  make test-versions - Verify pinned versions are up to date"
	@echo "  make ci     - Run local CI checks"
	@echo "  make prod   - Run production server (nginx, port 8080)"
	@echo "  make stop   - Stop all running containers"
	@echo "  make clean  - Remove generated files"
	@echo "  make lint   - Run formatters and linters (Docker pre-commit)"

setup:
	@echo "🔧 Building Docker images..."
	@docker compose --profile dev --profile build --profile test --profile lint build
	@$(MAKE) hooks
	@echo "✅ Docker images are ready"

hooks:
	@echo "🪝 Configuring git hooks..."
	@chmod +x .githooks/pre-commit
	@git config --local core.hooksPath .githooks
	@echo "✅ Git hooks configured"

dev:
	@echo "🌐 Starting dev server..."
	@docker compose --profile dev up --build

build:
	@echo "🔨 Building site..."
	@docker compose --profile build run --rm build

test:
	@echo "🧪 Running tests..."
	@docker compose --profile test run --rm test

test-versions:
	@echo "🔎 Checking pinned versions..."
	@docker compose --profile lint run --rm lint ./scripts/check-versions.sh

ci:
	@echo "🧰 Running CI checks locally..."
	@$(MAKE) lint
	@$(MAKE) test
	@$(MAKE) test-versions

prod:
	@echo "🚀 Starting production server..."
	@docker compose --profile prod up --build -d

clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf public/ resources/ .hugo_build.lock
	@echo "✅ Clean complete"

lint:
	@echo "🔍 Running linters in Docker..."
	@docker compose --profile lint run --rm lint

stop:
	@echo "🛑 Stopping containers..."
	@docker compose down
