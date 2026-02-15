# ngsanogo.github.io

![Build and Deploy](https://github.com/ngsanogo/ngsanogo.github.io/workflows/Build%20and%20Deploy/badge.svg)

Personal site and blog — **Issa Sanogo**, Senior Data Engineer.

**Live:** [ngsanogo.github.io](https://ngsanogo.github.io)
**Stack:** Hugo + Docker + GitHub Actions

## Requirements

Docker + Docker Compose

## Usage

| Task | Command |
|------|---------|
| Dev server (hot reload) | `make dev` |
| Build site | `make build` |
| Run tests | `make test` |
| Production server | `make prod` |
| Clean output | `make clean` |
| Lint and format | `make lint` |

## Quick start

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io
make dev
```

Open http://localhost:1313

## Contributing

### Setup pre-commit hooks (recommended)

Install pre-commit to automatically check code quality before commits:

```bash
brew install pre-commit  # macOS
# or pip install pre-commit
pre-commit install
```

After installation, hooks will run automatically on `git commit` and fix issues like trailing whitespace.

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

Or run pre-commit on all files:

```bash
pre-commit run --all-files
```

## Deploy

Push to `main` → GitHub Actions builds and deploys to GitHub Pages.

## License

© Issa Sanogo — [ngsanogo.github.io](https://ngsanogo.github.io)
