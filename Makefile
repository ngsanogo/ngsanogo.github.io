.PHONY: setup hooks dev build test test-content test-versions ci prod clean lint stop new-post help

check-docker:
	@command -v docker >/dev/null 2>&1 || { \
		echo "❌ Docker is required but not found in PATH."; \
		echo "Install Docker Desktop or use the devcontainer, then retry."; \
		exit 127; \
	}

help:
	@echo "Available commands:"
	@echo "  make setup  - Build Docker images (first-time setup)"
	@echo "  make hooks  - Configure repository git hooks"
	@echo "  make dev    - Start dev server with hot reload (port 1313)"
	@echo "  make build  - Build the static site"
	@echo "  make test   - Build and validate output"
	@echo "  make test-content - Validate content front matter quality"
	@echo "  make test-versions - Verify pinned versions are up to date"
	@echo "  make ci     - Run local CI checks"
	@echo "  make prod   - Run production server (nginx, port 8080)"
	@echo "  make stop   - Stop all running containers"
	@echo "  make clean  - Remove generated files"
	@echo "  make lint   - Run formatters and linters (Docker pre-commit)"
	@echo "  make new-post TITLE=\"...\" - Create a new post file with standard front matter"

setup: check-docker
	@echo "🔧 Building Docker images..."
	@docker compose --profile dev --profile build --profile test --profile lint build
	@$(MAKE) hooks
	@echo "✅ Docker images are ready"

hooks:
	@echo "🪝 Configuring git hooks..."
	@chmod +x .githooks/pre-commit
	@git config --local core.hooksPath .githooks
	@echo "✅ Git hooks configured"

dev: check-docker
	@echo "🌐 Starting dev server..."
	@docker compose --profile dev up --build

build: check-docker
	@echo "🔨 Building site..."
	@docker compose --profile build run --rm build

test: check-docker
	@echo "🧪 Running tests..."
	@docker compose --profile test run --rm test

test-content:
	@echo "🧾 Validating content front matter..."
	@./scripts/validate-frontmatter.sh

test-versions: check-docker
	@echo "🔎 Checking pinned versions..."
	@docker compose --profile lint run --rm lint ./scripts/check-versions.sh

ci:
	@echo "🧰 Running CI checks locally..."
	@$(MAKE) lint
	@$(MAKE) test
	@$(MAKE) test-content
	@$(MAKE) test-versions

prod: check-docker
	@echo "🚀 Starting production server..."
	@docker compose --profile prod up --build -d

clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf public/ resources/ .hugo_build.lock
	@echo "✅ Clean complete"

lint: check-docker
	@echo "🔍 Running linters in Docker..."
	@docker compose --profile lint run --rm lint

stop: check-docker
	@echo "🛑 Stopping containers..."
	@docker compose down

new-post:
	@if [ -z "$(TITLE)" ]; then \
		echo "❌ Missing TITLE. Usage: make new-post TITLE=\"My New Post\""; \
		exit 1; \
	fi
	@slug="$$(printf '%s' "$(TITLE)" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$$//')"; \
	if [ -z "$$slug" ]; then \
		echo "❌ Could not derive a valid slug from TITLE."; \
		exit 1; \
	fi; \
	file="content/posts/$$slug.md"; \
	if [ -f "$$file" ]; then \
		echo "❌ Post already exists: $$file"; \
		exit 1; \
	fi; \
	printf '%s\n' \
		'---' \
		'title: "$(TITLE)"' \
		'slug: "'"$$slug"'"' \
		'date: "'"$$(date +%Y-%m-%d)"'"' \
		'description: ""' \
		'categories: []' \
		'tags: []' \
		'keywords: []' \
		'draft: true' \
		'series: ""' \
		'image: ""' \
		'---' \
		'' \
		'## Introduction' \
		'' > "$$file"; \
	echo "✅ Created $$file"
