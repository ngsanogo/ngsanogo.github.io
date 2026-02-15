# Security Policy

## Supported Versions

This project is a personal blog and portfolio site. Security updates are applied to the latest version only.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest | :x:               |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it privately.

**Email:** [ngsanogo@proton.me](mailto:ngsanogo@proton.me)

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Please do not:**
- Create public GitHub issues for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix and disclosure:** As soon as possible, depending on severity

## Security Considerations

This project:
- Uses Hugo to generate static HTML (no server-side execution)
- Deploys to GitHub Pages (read-only static hosting)
- Builds and tests run in Docker (multi-stage, minimal Alpine images)
- CI/CD validates output before deployment
- Production image runs nginx as non-root user

## Best Practices

When contributing or forking:
- Never commit secrets, API keys, or credentials
- Review Docker security best practices
- Keep Hugo and base images up to date (Dependabot is configured)

Thank you for helping keep this project secure.
