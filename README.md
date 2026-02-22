# ngsanogo.github.io

![Build and Deploy](https://github.com/ngsanogo/ngsanogo.github.io/workflows/Build%20and%20Deploy/badge.svg)

Personal site and blog — **Issa Sanogo**, Senior Data Engineer.

**Live:** [ngsanogo.github.io](https://ngsanogo.github.io)
**Stack:** Hugo + Docker + GitHub Actions

## Requirements

- Docker Desktop (includes Docker Compose)
- VS Code with Dev Containers extension (for devcontainer workflow)

**No local Python, Node.js, Hugo, or other tools required on macOS.**

## Quick start

👉 **New to this project?** Read [ONBOARDING.md](ONBOARDING.md) for detailed setup instructions.

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io
make setup  # builds Docker images & configures git hooks
make dev    # starts dev server at http://localhost:1313
```

## Dev container workflow

Development is designed to run inside the devcontainer.

1. Open this repository in VS Code
2. Run **Dev Containers: Reopen in Container**
3. In the container terminal, run:

```bash
make setup
make dev
```

You can commit from:
- macOS terminal (host)
- devcontainer terminal

In both cases, the same repository hook runs `pre-commit` automatically.

## Usage

| Task | Command |
|------|---------|
| Build Docker images | `make setup` |
| Configure git hooks only | `make hooks` |
| Dev server (hot reload) | `make dev` |
| Build site | `make build` |
| Run tests | `make test` |
| Production server | `make prod` |
| Stop containers | `make stop` |
| Clean output | `make clean` |
| Lint and format | `make lint` |

## Contributing

### Zero-install workflow (Docker only)

All development commands run in Docker or in the devcontainer. No Python/Node tools are required on macOS.

```bash
make setup   # build images
make dev     # run Hugo dev server
make build   # build static site
make test    # validate output
make lint    # run pre-commit checks in Docker
```

### Commit and pre-commit behavior

- On macOS: `git commit` triggers `.githooks/pre-commit`, which runs checks in Docker
- In devcontainer: `git commit` triggers the same hook, which runs local `pre-commit` in the container
- To configure the hook path: `make hooks` (already included in `make setup`)

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

## Deploy

Push to `main` → GitHub Actions builds and deploys to GitHub Pages.

## License

© Issa Sanogo — [ngsanogo.github.io](https://ngsanogo.github.io)
