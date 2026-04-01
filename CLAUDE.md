# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal French blog on data engineering, built with Hugo 0.157.0 and deployed to GitHub Pages. All tooling runs in Docker — no local Hugo, Node.js, or Python installation required.

## Commands

All commands route through Docker Compose via `make`. Docker Desktop is the only local requirement.

```bash
make setup          # Build Docker images and configure git hooks (run once)
make dev            # Dev server with hot reload at http://localhost:1313
make build          # Build static site (Hugo + minification)
make lint           # Run pre-commit hooks (formatters and linters)
make fix            # Auto-fix formatting issues (Prettier, markdownlint)
make test           # Build and validate output (index.html, sitemap.xml)
make test-content   # Validate post front matter quality
make test-links     # Validate links in HTML and Markdown (Lychee)
make test-secrets   # Scan for leaked secrets (gitleaks)
make test-unit      # Unit tests for front matter validation script
make ci             # Full local CI pipeline (lint → test → test-content → test-links → test-secrets → test-unit)
make clean          # Remove public/, resources/, .hugo_build.lock
make stop           # Stop all Docker containers
```

### Creating content

```bash
make new-post TITLE="My Post Title"   # Creates post with full front matter template
```

## Architecture

### Content structure

- `content/posts/` — Blog articles (data engineering, French)
- `content/about/` — About page
- Permalinks: `/posts/:slug/`

### Front matter requirements (enforced by `scripts/validate-frontmatter.sh`)

Every post in `content/posts/` must have:

- `title`: min 10 characters
- `slug`: lowercase alphanumeric with hyphens, unique across all posts
- `date`: `YYYY-MM-DD` format
- `description`: min 100 characters (SEO requirement)
- `categories`, `tags`, `keywords`: non-empty
- `image`: absolute path (`/...`) or full URL (`http...`)

Validation runs automatically as a pre-commit hook and via `make test-content`.

### Docker Compose profiles

`docker-compose.yml` defines four services with profiles:

- `dev` — Hugo server (port 1313, poll-based file watching)
- `build` — Hugo build with minification
- `test` — Hugo build + output validation
- `lint` — pre-commit with cache volume

### Linting stack

Configured in `.pre-commit-config.yaml`:

- **editorconfig-checker** — Whitespace/encoding consistency
- **yamllint** — YAML validation (`.yamllint.yml`: line-length and truthy checks disabled)
- **markdownlint** — Markdown style (`.markdownlint.yml`: MD013, MD033, MD041, MD060 disabled)
- **Prettier** — CSS, JS, JSON, YAML formatting
- **validate-frontmatter.sh** — Custom post metadata validation

### CI/CD

- **ci.yml**: Runs on push/PR to `main` — builds images, runs full quality suite
- **deploy.yml**: Triggers after CI succeeds on `main` — builds and deploys to GitHub Pages

### Custom layouts

No external theme. All templates are in the `layouts/` directory.
