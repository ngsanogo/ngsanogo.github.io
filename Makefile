.PHONY: build test dev clean all help coverage docker-build docker-test docker-dev

help:
	@echo "Available commands:"
	@echo "  make build         - Build the site"
	@echo "  make test          - Run all tests"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make dev           - Build and start dev server"
	@echo "  make clean         - Clean generated files and cache"
	@echo "  make all           - Clean, test, and build"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-test   - Run tests in Docker"
	@echo "  make docker-dev    - Run dev server in Docker"

build:
	@echo "🔨 Building site..."
	@python3 src/build.py

test:
	@echo "🧪 Running tests..."
	@python3 -m unittest discover tests/ -v

coverage:
	@echo "📊 Running tests with coverage..."
	@command -v coverage >/dev/null 2>&1 || { echo "⚠️  coverage not installed. Install with: pip3 install coverage"; exit 1; }
	@python3 -m coverage run -m unittest discover tests/
	@python3 -m coverage report
	@python3 -m coverage html
	@echo "✅ Coverage report generated in htmlcov/"

dev: build
	@echo "🌐 Starting dev server..."
	@python3 src/dev.py

clean:
	@echo "🧹 Cleaning generated files and cache..."
	@rm -rf public/ __pycache__/ src/__pycache__/ tests/__pycache__/ .venv/__pycache__/
	@rm -rf htmlcov/ .coverage
	@rm -f test_*.md
	@echo "✅ Clean complete"

all: clean test build
	@echo "✅ All tasks complete"

docker-build:
	@echo "🐳 Building site in Docker..."
	@docker compose --profile build run --rm build

docker-test:
	@echo "🧪 Running tests in Docker..."
	@docker compose --profile test run --rm test

docker-dev:
	@echo "🌐 Starting dev server in Docker..."
	@docker compose --profile dev up --build
