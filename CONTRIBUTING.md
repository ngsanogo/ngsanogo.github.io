# Contributing

## Branch workflow (simplified GitFlow)

- `main` stays deployable at all times.
- Create branches from `main` using `feature/<short-name>` or `fix/<short-name>`.
- Open a Pull Request to `main`.
- Merge with **Squash and merge** after CI is green.

## Pull request rules

- Keep each PR focused on a single concern.
- Do not mix refactor and feature changes unless required.
- Include validation evidence (`make lint`, `make test`, and when relevant `make test-versions`).
- Update docs when workflow or behavior changes.

## Local workflow

```bash
make setup
make lint
make test
make test-versions
```
