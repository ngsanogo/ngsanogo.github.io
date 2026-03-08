# Architecture and Maintenance Strategy

## Goal

Keep a fast, reliable, low-complexity Hugo platform focused on content quality, SEO, and reproducible operations.

## Architecture Principles

- Static-first: Hugo.
- Single repository, no runtime database.
- Docker-first reproducibility for build/lint/test.
- Quality gates before publication.
- Small reusable templates over duplicated layout logic.

## Repository Structure Rules

- `content/`: all editorial pages and posts.
- `layouts/`: Hugo templates and reusable partials.
- `assets/`: CSS and JavaScript source files.
- `static/`: files copied as-is to output.
- `scripts/`: project automation and validation scripts.
- `docs/`: governance and contributor guidance.

## Content Workflow

1. Create a draft with `make new-post TITLE="..."`.
2. Fill required front matter (`title`, `slug`, `date`, `description`, `categories`, `tags`).
3. Write content and internal links.
4. Run `make test-content`.
5. Run `make lint` and `make test`.
6. Open PR with validation evidence.

## Quality Gates

- Pre-commit checks style, markdown, yaml/json, and front matter completeness.
- Local checks are the primary gate: `make lint`, `make test`, `make test-content`.
- Optional remote CI can be triggered manually when needed.

## SEO Rules

- Every post must have a non-empty `description`.
- Description must be at least 100 characters.
- Prefer explicit `keywords`, `image`, and `series` when relevant.
- Keep slugs short and stable once published.
- Use internal linking between related articles.

## Security Rules

- Never commit real credentials.
- Keep sample credentials only in clearly educational snippets.
- Review workflow permissions and keep them minimal.

## Operational Cadence

- Weekly: review failed checks and fix regressions.
- Monthly: dependency updates when needed.
- Quarterly: content taxonomy cleanup and template debt review.
