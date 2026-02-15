# ngsanogo.github.io

![Build and Deploy](https://github.com/ngsanogo/ngsanogo.github.io/workflows/Build%20and%20Deploy/badge.svg)

Personal site and blog — **Issa Sanogo**, Senior Data Engineer.

**Live:** [ngsanogo.github.io](https://ngsanogo.github.io)
**Stack:** Hugo + Docker + GitHub Actions

## Requirements

Docker + Docker Compose

## Usage

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

## Deploy

Push to `main` → GitHub Actions builds and deploys to GitHub Pages.

## License

© Issa Sanogo — [ngsanogo.github.io](https://ngsanogo.github.io)
