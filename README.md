# ngsanogo.github.io

![Build and Deploy](https://github.com/ngsanogo/ngsanogo.github.io/workflows/Build%20and%20Deploy/badge.svg)

Personal site and blog — **Issa Sanogo**, Senior Data Engineer.

**Live:** [ngsanogo.github.io](https://ngsanogo.github.io)
**Stack:** Hugo + Docker + GitHub Actions

## Vision

This repository provides a production-ready technical blog platform with a strict Docker-first workflow.

Goals:

- keep local setup near zero,
- enforce reproducible builds,
- keep contribution and maintenance standards clear and lightweight.

## Architecture

- **Site engine:** Hugo
- **Runtime:** Nginx (containerized)
- **Automation:** Makefile + Docker Compose profiles (`dev`, `build`, `test`, `lint`, `prod`)
- **Quality gate:** pre-commit (Ruff, YAML/Markdown/JSON checks, Prettier)
- **CI/CD:** GitHub Actions (`CI`, `Secrets Scan`, `Build and Deploy`)

## Requirements

- Docker Desktop (includes Docker Compose)
- VS Code with Dev Containers extension (for devcontainer workflow)

**No local Python, Node.js, Hugo, or other tools required on macOS.**

## Quick start (Docker)

👉 **New to this project?** Read [ONBOARDING.md](ONBOARDING.md) for detailed setup instructions.

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io
make setup  # builds Docker images & configures git hooks
make dev    # starts dev server at http://localhost:1313
```

## Daily commands

| Task                     | Command              |
| ------------------------ | -------------------- |
| Build Docker images      | `make setup`         |
| Configure git hooks only | `make hooks`         |
| Dev server (hot reload)  | `make dev`           |
| Build site               | `make build`         |
| Run tests                | `make test`          |
| Validate post metadata   | `make test-content`  |
| Verify pinned versions   | `make test-versions` |
| Run CI checks locally    | `make ci`            |
| Production server        | `make prod`          |
| Stop containers          | `make stop`          |
| Clean output             | `make clean`         |
| Lint and format          | `make lint`          |
| Create a new blog post   | `make new-post TITLE="..."` |

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

## Repository map

- `content/`: source content (posts/pages)
- `layouts/`, `assets/`, `static/`: Hugo presentation layers
- `.github/workflows/`: CI/CD and security automation
- `scripts/`: operational scripts (version checks)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch and PR workflow.
See [docs/ARCHITECTURE_STRATEGY.md](docs/ARCHITECTURE_STRATEGY.md) for long-term architecture and maintenance strategy.

## Deploy

Push to `main` → GitHub Actions builds and deploys to GitHub Pages.

## License

MIT License. See `LICENSE`.
