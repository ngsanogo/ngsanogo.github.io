# ngsanogo.github.io

![Build and Deploy](https://github.com/ngsanogo/ngsanogo.github.io/workflows/Build%20and%20Deploy/badge.svg)
![Hugo](https://img.shields.io/badge/Hugo-0.143-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Personal site and blog: **Issa Sanogo** — Senior Data Engineer. Data platforms, data quality, technical writing.

- **Live site:** [https://ngsanogo.github.io](https://ngsanogo.github.io)
- **Stack:** Hugo (static site generator), Docker, GitHub Actions → GitHub Pages

---

## Architecture

```
ngsanogo.github.io/
├── content/                # Source content (Markdown + YAML frontmatter)
│   ├── _index.md           # Homepage metadata
│   ├── about.md
│   ├── cv.md
│   ├── contact.md
│   ├── projects.md
│   └── posts/              # Blog posts
│       └── _index.md       # Blog listing metadata
├── layouts/                # Hugo templates
│   ├── _default/           # Base templates (baseof, single, list)
│   ├── posts/              # Post-specific templates
│   ├── partials/           # Reusable components (head, header, footer)
│   ├── index.html          # Homepage template
│   └── 404.html            # Error page
├── assets/                 # Processed by Hugo Pipes
│   ├── css/main.css        # Site styles
│   └── js/copy-code.js     # Copy button for code blocks
├── static/                 # Copied as-is to public/
│   ├── favicon.svg
│   └── robots.txt
├── hugo.toml               # Site configuration
├── Dockerfile              # Multi-stage: Hugo build + nginx production
├── docker-compose.yml      # dev, build, test, prod services
├── Makefile                # Shortcuts for Docker commands
└── .github/workflows/
    └── deploy.yml          # CI: Docker build → validate → deploy to Pages
```

---

## Requirements

- **Docker + Docker Compose** — required for build/dev/test/prod.
- **Optional (linting):** Python 3.12+ and `pre-commit`.

---

## Usage

| Task | Command |
|------|---------|
| Dev server (hot reload) | `make dev` |
| Build site | `make build` |
| Run tests | `make test` |
| Production server | `make prod` |
| Clean output | `make clean` |
| Lint and format | `make lint` |

### Quick start

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io
make dev
```

Open **http://localhost:1313**. Stop with `Ctrl+C`.

### Add a new post

Create `content/posts/my-post.md` with YAML frontmatter:

```yaml
---
title: "My Post Title"
slug: my-post
date: 2026-01-01
description: "Short description for listing page."
draft: false
---

## First Section

Content here...
```

Then rebuild: `make build`.

---

## Quality (optional)

Install pre-commit and run all hooks:

```bash
python3 -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Deploy (GitHub Pages)

Push to `main`. GitHub Actions builds the site in Docker, validates output, checks links (Lychee), and deploys `public/` to GitHub Pages automatically.

---

## License and contact

Content and code © Issa Sanogo. See the [site](https://ngsanogo.github.io) or [contact page](https://ngsanogo.github.io/contact).
