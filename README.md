# ngsanogo.github.io

![Build and Deploy](https://github.com/ngsanogo/ngsanogo.github.io/workflows/Build%20and%20Deploy/badge.svg)

Personal site and blog — **Issa Sanogo**, Senior Data Engineer.

**Live:** [ngsanogo.github.io](https://ngsanogo.github.io)
**Stack:** Hugo + Docker + GitHub Actions

## Requirements

- Docker + Docker Compose
- Python 3.12+ (for local linting with pre-commit)

## Quick start

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io

# Setup dev environment (venv + pre-commit hooks)
make setup

# Start dev server
make dev
```

Open http://localhost:1313

## Usage

| Task | Command |
|------|---------|
| Setup dev environment | `make setup` |
| Dev server (hot reload) | `make dev` |
| Build site | `make build` |
| Run tests | `make test` |
| Production server | `make prod` |
| Clean output | `make clean` |
| Lint and format | `make lint` |

## Contributing

### First-time setup

Run `make setup` to create a Python virtual environment and install pre-commit hooks:

```bash
make setup
```

This will:
- Create a `.venv` directory with isolated Python dependencies
- Install pre-commit and other dev tools
- Setup git hooks to automatically check code quality before commits

**Note:** All tools run in the venv - nothing is installed globally on your system.

### Adding a new blog post

Create a new markdown file in `content/posts/` with YAML frontmatter:

```markdown
---
title: "Your Post Title"
slug: your-post-slug
date: 2026-02-15
description: "Brief description of your post"
categories: ["category"]
tags: ["tag1", "tag2"]
draft: false
---

Your content here...
```

### Running linting locally

Run all linters and formatters:

```bash
make lint
```

Or run pre-commit directly (from venv):

```bash
.venv/bin/pre-commit run --all-files
```

## Deploy

Push to `main` → GitHub Actions builds and deploys to GitHub Pages.

## License

© Issa Sanogo — [ngsanogo.github.io](https://ngsanogo.github.io)
