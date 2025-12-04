# Pre-commit Setup for Markdown Files

This repository uses pre-commit hooks to automatically lint and format markdown files before each commit.

## What It Does

- **Markdown Linting**: Checks markdown files for common issues and fixes them automatically
- **Formatting**: Ensures consistent formatting across all markdown files
- **Whitespace Cleanup**: Removes trailing whitespace and ensures proper line endings
- **File Endings**: Ensures all files end with a newline

## Setup (One-Time)

### On Windows (PowerShell)

```powershell
.\setup-precommit.ps1
```

### On Linux/Mac

```bash
chmod +x setup-precommit.sh
./setup-precommit.sh
```

### Manual Setup

If the scripts don't work:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Optional: Run on all existing files
pre-commit run --all-files
```

## How It Works

Once set up, pre-commit will automatically run every time you `git commit`:

1. You stage files: `git add .`
2. You commit: `git commit -m "message"`
3. Pre-commit automatically runs and formats your markdown files
4. If files were modified, you'll need to stage them again and re-commit
5. If no issues, commit proceeds normally

## Manual Usage

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Skip pre-commit for a specific commit (not recommended)
git commit --no-verify -m "message"
```

## Configuration Files

- `.pre-commit-config.yaml` - Main configuration
- `.markdownlint.json` - Markdown linting rules
- `.prettierrc` - Prettier formatting options

## Customization

Edit `.markdownlint.json` to change markdown linting rules:

```json
{
  "default": true,
  "MD013": false, // Disable line length rule
  "MD033": false, // Allow HTML in markdown
  "MD041": false // First line doesn't need to be H1
}
```

Edit `.prettierrc` to change formatting options:

```json
{
  "proseWrap": "preserve", // Don't wrap prose
  "printWidth": 120 // Maximum line width
}
```

## Troubleshooting

**Pre-commit command not found:**

- Make sure Python and pip are installed
- Try: `pip install --user pre-commit`
- Add Python Scripts to PATH

**Hooks not running:**

- Run: `pre-commit install`
- Check: `git config core.hooksPath` (should be empty or `.git/hooks`)

**Too many changes on first run:**

- This is normal - existing files are being formatted
- Review changes, commit them, then future commits will be smaller

## Uninstalling

```bash
# Remove git hooks
pre-commit uninstall

# Remove pre-commit package
pip uninstall pre-commit
```
