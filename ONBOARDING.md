# Onboarding — Zero-install Workflow

This project requires **zero local installation** beyond Docker Desktop and VS Code.

## Prerequisites

- Docker Desktop for macOS (includes Docker Compose)
- VS Code with **Dev Containers** extension

## First-time setup

### Option 1: Dev container (recommended)

```bash
# Clone the repository
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io

# Open in VS Code
code .

# In VS Code command palette (Cmd+Shift+P):
# > Dev Containers: Reopen in Container
```

Once inside the container:

```bash
make setup  # builds Docker images and configures git hooks
make dev    # starts Hugo dev server at http://localhost:1313
```

### Option 2: Host development (macOS)

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io
make setup
make dev
```

All commands run in Docker containers — no Hugo, Python, or Node.js required on macOS.

## Daily workflow

| Task | Command |
|------|---------|
| Start dev server | `make dev` |
| Build static site | `make build` |
| Run tests | `make test` |
| Validate post metadata | `make test-content` |
| Lint and format | `make lint` |
| Stop containers | `make stop` |
| Clean build artifacts | `make clean` |

## Post quality contract

Each post in `content/posts/` must include:

- `title`
- `slug` (lowercase + hyphens)
- `date` (`YYYY-MM-DD`)
- `description` (minimum 100 characters)
- `categories`
- `tags`
- `keywords`
- `series`
- `image` (absolute path like `/images/...` or full URL)

## Commit workflow

Git hooks are configured automatically via `make setup`.

- **From macOS**: `git commit` runs pre-commit checks in Docker
- **From devcontainer**: `git commit` runs pre-commit checks natively in the container

Both paths use the same repository-managed hook (`.githooks/pre-commit`).

## Verifying reproducibility

```bash
# Fresh clone test
rm -rf /tmp/test-clone
git clone https://github.com/ngsanogo/ngsanogo.github.io.git /tmp/test-clone
cd /tmp/test-clone
make setup
make test
make lint
```

If all commands succeed, the environment is 100% reproducible.

## CI/CD

GitHub Actions uses the same Docker workflow:
- Lint: `docker compose --profile lint run --rm lint`
- Build: `docker compose --profile build run --rm build`
- Deploy: automated on push to `main`

## Troubleshooting

**Problem**: `make dev` fails with port conflict

```bash
make stop
# or manually: docker compose down
make dev
```

**Problem**: Git hooks not running

```bash
make hooks
```

**Problem**: Stale Docker build cache

```bash
docker compose build --no-cache --profile dev --profile lint
```

## File structure

```
.
├── .devcontainer/         # VS Code Dev Container config
├── .githooks/             # Repository-managed git hooks
├── .github/workflows/     # CI/CD pipelines
├── content/               # Hugo content (markdown)
├── layouts/               # Hugo templates
├── assets/                # CSS, JS
├── static/                # Static files (robots.txt, etc.)
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Service definitions (dev, build, lint, prod)
├── Makefile               # Convenience commands
└── hugo.toml              # Hugo configuration
```

## Next steps

- Read [README.md](README.md) for detailed usage
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines (if exists)
- Visit the [live site](https://ngsanogo.github.io)
