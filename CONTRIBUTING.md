# Contributing

## Branch workflow (simplified GitFlow)

- `main` stays deployable at all times.
- Create branches from `main` using `feature/<short-name>` or `fix/<short-name>`.
- Open a Pull Request to `main`.
- Merge with **Squash and merge** after CI is green.

## Local workflow

```bash
make setup
make lint
make test
make test-versions
```

## Pull Request expectations

- Keep scope small and focused.
- Explain why the change is needed.
- Document operational impact (build, deploy, security) when relevant.
- Update docs only when behavior or workflow changes.
