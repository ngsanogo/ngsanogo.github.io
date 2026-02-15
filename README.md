# ngsanogo.github.io

![Build and Deploy](https://github.com/ngsanogo/ngsanogo.github.io/workflows/Build%20and%20Deploy/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Personal site and blog: **Issa Sanogo** — Senior Data Engineer. Data platforms, data quality, technical writing.

- **Live site:** [https://ngsanogo.github.io](https://ngsanogo.github.io)
- **Stack:** Python 3.11 (stdlib only), Markdown → HTML, GitHub Actions → GitHub Pages

---

## Description

Static site generated from Markdown: homepage, blog with pagination, static pages (About, Resume, Contact, Projects), sitemap, and SEO (meta, Open Graph, Schema.org). No JavaScript framework, no database. Content lives in `content/`; build writes to `public/`.

---

## Architecture

```
ngsanogo.github.io/
├── src/                    # Generator and server
│   ├── build.py            # Builds site (markdown → HTML, sitemap, copy static)
│   ├── config.py           # Site title, URL, nav, posts per page
│   ├── template.html       # HTML shell (placeholders: {{title}}, {{content}}, etc.)
│   ├── style.css           # Inlined into pages at build time
│   ├── dev.py              # Local HTTP server (serves public/)
│   └── static/             # Copied as-is to public/
│       ├── robots.txt
│       ├── 404.html
│       └── favicon.svg
├── content/                # Source content
│   ├── posts/              # Blog posts (*.md with YAML frontmatter)
│   │   └── _template.md    # Template for new posts
│   ├── about.md
│   ├── cv.md
│   ├── contact.md
│   └── projects.md
├── tests/
│   └── test_build.py       # Unit and integration tests
├── public/                 # Generated output (gitignored)
├── .github/workflows/
│   └── deploy.yml          # CI: test → build → Lychee (links) → deploy to Pages
├── Dockerfile              # Python 3.11-slim, non-root user
├── docker-compose.yml      # test, build, dev services
├── Makefile                # build, test, dev, clean, all
└── .env.example            # Optional dev server overrides
```

**Responsibilities:**

- **build.py** — Single entry for building the site: parse content, render HTML, write `public/`, sitemap, copy static files.
- **config.py** — Central config (no env required; optional overrides via env in dev).
- **dev.py** — Serve `public/` on a configurable host/port for local preview.

---

## Requirements

- **Python 3.11+** (local) **or** **Docker + Docker Compose** (no local Python).

---

## Installation (from scratch)

### Option A — Docker (recommended if you don’t want to install Python)

1. Clone the repo and enter it:
   ```bash
   git clone https://github.com/ngsanogo/ngsanogo.github.io.git
   cd ngsanogo.github.io
   ```
2. Run tests and build:
   ```bash
   docker compose --profile test run --rm test
   docker compose --profile build run --rm build
   ```
3. Serve locally:
   ```bash
   docker compose --profile dev up --build
   ```
   Open **http://localhost:8000**. Stop with `Ctrl+C`.

### Option B — Local Python

1. Clone and enter the repo (same as above).
2. Ensure Python 3.11+ is installed:
   ```bash
   python3 --version
   ```
3. From the project root:
   ```bash
   python3 -m unittest discover tests/ -v
   python3 src/build.py
   python3 src/dev.py
   ```
   Open **http://localhost:8000**.

---

## Usage

| Task | Docker | Local |
|------|--------|--------|
| Run tests | `docker compose --profile test run --rm test` | `python3 -m unittest discover tests/ -v` or `make test` |
| Build site | `docker compose --profile build run --rm build` | `python3 src/build.py` or `make build` |
| Preview (build + serve) | `docker compose --profile dev up --build` | `make dev` (or build then `python3 src/dev.py`) |
| Clean + test + build | — | `make all` |

- **Add a post:** Copy `content/posts/_template.md` to `content/posts/my-slug.md`, set `title`, `slug`, `date`, `description`, `draft: false`, then build.
- **Edit pages:** Edit `content/about.md`, `cv.md`, `contact.md`, `projects.md` (YAML frontmatter with `title`, optional `description`).
- **Optional env:** Set `DEV_SERVER_HOST` or `DEV_SERVER_PORT` in your environment (e.g. copy `.env.example` to `.env` and `source .env`, or export in your shell) to override the dev server.

---

## Deploy (GitHub Pages)

1. **Local:** `make all` (or run tests + build as above).
2. **Commit and push** to `main` or `dev`.
3. GitHub Actions runs tests, builds the site, checks links (Lychee), and deploys `public/` to GitHub Pages. No manual upload.

---

## License and contact

Content and code © Issa Sanogo. For contact, see the [site](https://ngsanogo.github.io) or [contact page](https://ngsanogo.github.io/contact).
