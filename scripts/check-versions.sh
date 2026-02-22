#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRECOMMIT_FILE="$ROOT_DIR/.pre-commit-config.yaml"
DOCKERFILE_FILE="$ROOT_DIR/Dockerfile"
DEVCONTAINER_DOCKERFILE_FILE="$ROOT_DIR/.devcontainer/Dockerfile"

extract_hugo_version() {
  local file="$1"
  awk -F'=' '/^ARG HUGO_VERSION=/{print $2; exit}' "$file"
}

extract_node_major() {
  local file="$1"
  awk -F'=' '/^ARG NODE_MAJOR=/{print $2; exit}' "$file"
}

extract_prettier_version() {
  local file="$1"
  awk -F'=' '/^ARG PRETTIER_VERSION=/{print $2; exit}' "$file"
}

extract_rev_for_repo() {
  local repo="$1"
  awk -v repo="$repo" '
    $0 ~ "repo: " repo {
      getline
      if ($1 == "rev:") {
        print $2
        exit
      }
    }
  ' "$PRECOMMIT_FILE"
}

latest_release_tag() {
  local repo="$1"
  curl -fsSL "https://api.github.com/repos/$repo/releases/latest" \
    | sed -n 's/.*"tag_name": "\([^"]*\)".*/\1/p' \
    | head -n1
}

latest_npm_version() {
  local package="$1"
  npm view "$package" version
}

assert_equal() {
  local actual="$1"
  local expected="$2"
  local label="$3"

  if [[ "$actual" != "$expected" ]]; then
    echo "❌ $label: expected '$expected' but found '$actual'"
    exit 1
  fi

  echo "✅ $label: $actual"
}

docker_hugo="$(extract_hugo_version "$DOCKERFILE_FILE")"
devcontainer_hugo="$(extract_hugo_version "$DEVCONTAINER_DOCKERFILE_FILE")"
latest_hugo="$(latest_release_tag "gohugoio/hugo")"
latest_hugo="${latest_hugo#v}"
node_major="$(extract_node_major "$DEVCONTAINER_DOCKERFILE_FILE")"
docker_prettier="$(extract_prettier_version "$DOCKERFILE_FILE")"
devcontainer_prettier="$(extract_prettier_version "$DEVCONTAINER_DOCKERFILE_FILE")"
latest_prettier="$(latest_npm_version "prettier")"

assert_equal "$devcontainer_hugo" "$docker_hugo" "HUGO_VERSION sync (Dockerfile/devcontainer)"
assert_equal "$docker_hugo" "$latest_hugo" "HUGO_VERSION up to date"

if [[ -z "$node_major" ]]; then
  echo "❌ NODE_MAJOR is missing in .devcontainer/Dockerfile"
  exit 1
fi

if (( node_major < 20 )); then
  echo "❌ NODE_MAJOR must be >= 20 for markdownlint-cli compatibility (found $node_major)"
  exit 1
fi

echo "✅ NODE_MAJOR compatibility: $node_major"

assert_equal "$devcontainer_prettier" "$docker_prettier" "PRETTIER_VERSION sync (Dockerfile/devcontainer)"
assert_equal "$docker_prettier" "$latest_prettier" "PRETTIER_VERSION up to date"

assert_equal "$(extract_rev_for_repo "https://github.com/astral-sh/ruff-pre-commit")" "$(latest_release_tag "astral-sh/ruff-pre-commit")" "ruff-pre-commit rev"
assert_equal "$(extract_rev_for_repo "https://github.com/pre-commit/pre-commit-hooks")" "$(latest_release_tag "pre-commit/pre-commit-hooks")" "pre-commit-hooks rev"
assert_equal "$(extract_rev_for_repo "https://github.com/editorconfig-checker/editorconfig-checker.python")" "$(latest_release_tag "editorconfig-checker/editorconfig-checker.python")" "editorconfig-checker rev"
assert_equal "$(extract_rev_for_repo "https://github.com/adrienverge/yamllint")" "$(latest_release_tag "adrienverge/yamllint")" "yamllint rev"
assert_equal "$(extract_rev_for_repo "https://github.com/igorshubovych/markdownlint-cli")" "$(latest_release_tag "igorshubovych/markdownlint-cli")" "markdownlint-cli rev"

echo "🎉 All pinned versions are up to date."
