# Contributing

## Branch workflow (simplified GitFlow)

- `main` stays deployable at all times.
- Create branches from `main` using `feature/<short-name>` or `fix/<short-name>`.
- Open a Pull Request to `main`.
- Merge with **Squash and merge** after CI is green.

## Pull request rules

- Keep each PR focused on a single concern.
- Do not mix refactor and feature changes unless required.
- Include validation evidence (`make lint`, `make test`).
- Include content validation evidence (`make test-content`) for post changes.
- Update docs when workflow or behavior changes.

## Local workflow

```bash
make setup
make lint
make test
make test-content

# Optional helper for new articles
make new-post TITLE="your title"
```

## Post metadata rules

For files in `content/posts/` (except `_index.md`), keep these fields present and valid:

- `slug`: lowercase and hyphenated
- `date`: `YYYY-MM-DD`
- `description`: at least 100 characters
- `image`: absolute path (`/images/...`) or full URL
