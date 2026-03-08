# ngsanogo.github.io

Personal site and blog — **Issa Sanogo**.

**Live:** [ngsanogo.github.io](https://ngsanogo.github.io)
**Stack:** Hugo + Docker

## Architecture

- **Site engine:** Hugo
- **Automation:** Makefile + Docker Compose profiles (`dev`, `build`, `test`, `lint`)
- **Quality gate:** pre-commit (YAML/Markdown/JSON checks, Prettier)
- **Deploy:** GitHub Actions (`Deploy Pages`)

## Requirements

- Docker Desktop (includes Docker Compose)
- VS Code with Dev Containers extension (for devcontainer workflow)

**No local Python, Node.js, Hugo, or other tools required on macOS.**

## Quick start (Docker)

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
| Run local full checks    | `make ci`            |
| Stop containers          | `make stop`          |
| Clean output             | `make clean`         |
| Lint and format          | `make lint`          |
| Create a new blog post   | `make new-post TITLE="..."` |

## Deployment

Push to `main` triggers GitHub Pages deployment.

## Repository map

- `content/`: source content (posts/pages)
- `layouts/`, `assets/`, `static/`: Hugo presentation layers
- `.github/workflows/`: deployment workflow
- `scripts/`: operational scripts

## License

MIT License. See `LICENSE`.
