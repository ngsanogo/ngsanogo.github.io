# Quick Reference — Zero-install Workflow

## First-time setup (macOS)

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io
make setup
```

## Daily development

```bash
make dev      # http://localhost:1313 (auto-reload)
make build    # generate static site in public/
make test     # validate build output
make lint     # run all code quality checks
```

## Git workflow

```bash
git add .
git commit -m "your message"  # pre-commit runs automatically via Docker
git push
```

## Devcontainer (VS Code)

```bash
# In VS Code command palette (Cmd+Shift+P)
> Dev Containers: Reopen in Container

# Then in terminal
make setup
make dev
```

## Production testing

```bash
make prod     # runs nginx on port 8080
make stop     # stops all containers
```

## Troubleshooting

```bash
# Port conflict
make stop && make dev

# Stale cache
docker compose build --no-cache --profile dev --profile lint

# Reset hooks
make hooks

# Clean build artifacts
make clean
```

## File structure

```
.
├── .devcontainer/         # VS Code Dev Container
├── .githooks/             # Repository-managed git hooks
├── .github/workflows/     # CI/CD
├── content/posts/         # Blog posts (markdown)
├── layouts/               # Hugo templates
├── assets/css/            # Styles
├── static/                # Static files
├── Dockerfile             # Multi-stage build
├── docker-compose.yml     # Services (dev/build/lint/prod)
├── Makefile               # Commands
├── hugo.toml              # Hugo config
├── ONBOARDING.md          # Detailed setup guide
└── CHANGELOG.md           # Migration history
```

## All make targets

| Command | Description |
|---------|-------------|
| `make help` | Show all commands |
| `make setup` | Build Docker images + configure hooks |
| `make hooks` | Configure git hooks only |
| `make dev` | Dev server with hot reload |
| `make build` | Build static site |
| `make test` | Validate build output |
| `make lint` | Run linters and formatters |
| `make prod` | Start production nginx server |
| `make stop` | Stop all containers |
| `make clean` | Remove build artifacts |

## Docker images

```bash
docker images | grep ngsanogo

ngsanogogithubio-build  # Hugo (Alpine)
ngsanogogithubio-lint   # Python 3.12 + pre-commit
ngsanogogithubio-test   # Hugo (Alpine)
ngsanogogithubio-prod   # nginx (Alpine)
```

## Zero install guarantee

**Required on macOS:**
- Docker Desktop

**Not required (everything runs in Docker):**
- ❌ Python
- ❌ Hugo
- ❌ Node.js / npm
- ❌ pre-commit
- ❌ Any other CLI tool

## Links

- **Live site:** https://ngsanogo.github.io
- **Detailed guide:** [ONBOARDING.md](ONBOARDING.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
