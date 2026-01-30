.PHONY: build test dev clean all help install

help:
	@echo "Available commands:"
	@echo "  make build    - Build the site"
	@echo "  make test     - Run all tests"
	@echo "  make dev      - Build and start dev server"
	@echo "  make clean    - Clean generated files"
	@echo "  make all      - Clean, test, and build"
	@echo "  make deploy   - Build, test, and push to GitHub"

build:
	@echo "🔨 Building site..."
	@python3 src/build.py

test:
	@echo "🧪 Running tests..."
	@python3 -m unittest discover tests/ -v

dev: build
	@echo "🌐 Starting dev server..."
	@python3 src/dev.py

clean:
	@echo "🧹 Cleaning generated files..."
	@rm -rf public/ __pycache__/ src/__pycache__/ tests/__pycache__/
	@rm -f test_*.md
	@echo "✅ Clean complete"

all: clean test build
	@echo "✅ All tasks complete"

deploy: all
	@echo "📦 Deploying to GitHub..."
	@git add -A
	@git status
	@read -p "Commit message: " msg; \
	git commit -m "$$msg"
	@git push
	@echo "✅ Deployed successfully"
