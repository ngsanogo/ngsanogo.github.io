.PHONY: setup hooks dev build test test-content test-links test-secrets ci clean lint stop new-post help

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
	@echo "  make test-links - Validate links in generated HTML and Markdown"
	@echo "  make test-secrets - Scan repository for leaked secrets"
	@echo "  make ci     - Run local CI checks"
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
	@docker compose --profile build run --rm -T build

test: check-docker
	@echo "🧪 Running tests..."
	@docker compose --profile test run --rm -T test

test-content: check-docker
	@echo "🧾 Validating content front matter..."
	@docker compose --profile lint run --rm -T lint ./scripts/validate-frontmatter.sh

test-links: check-docker
	@echo "🔗 Validating links in Docker..."
	@docker run --rm --entrypoint sh -v "$$PWD":/data lycheeverse/lychee:latest -lc 'find /data/content -name "*.md" -print0 | xargs -0 lychee --no-progress --accept "200..=299,429,999" --base-url https://ngsanogo.github.io --timeout 30 --max-retries 3 --retry-wait-time 2 --max-concurrency 16 --threads 8 --user-agent "Mozilla/5.0 (compatible; ngsanogo-link-check/1.0)" --'
	@docker run --rm --entrypoint sh -v "$$PWD":/data lycheeverse/lychee:latest -lc 'find /data/public -name "*.html" -print0 | xargs -0 lychee --offline --no-progress --base-url /data/public --timeout 10 --max-concurrency 16 --threads 8 --'

test-secrets: check-docker
	@echo "🔐 Scanning for secrets in Docker..."
	@docker run --rm -v "$$PWD":/repo -w /repo zricethezav/gitleaks:latest detect --source . --no-git --redact --verbose

ci:
	@echo "🧰 Running CI checks locally..."
	@$(MAKE) lint
	@$(MAKE) test
	@$(MAKE) test-content
	@$(MAKE) test-links
	@$(MAKE) test-secrets

clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf public/ resources/ .hugo_build.lock
	@echo "✅ Clean complete"

lint: check-docker
	@echo "🔍 Running linters in Docker..."
	@docker compose --profile lint run --rm -T lint

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
		'image: "/images/og-default.svg"' \
		'---' \
		'' \
		'## Introduction' \
		'' > "$$file"; \
	echo "✅ Created $$file"
