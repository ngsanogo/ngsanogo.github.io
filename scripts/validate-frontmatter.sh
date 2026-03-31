#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
POSTS_DIR="$ROOT_DIR/content/posts"

if [[ ! -d "$POSTS_DIR" ]]; then
  echo "❌ Missing posts directory: $POSTS_DIR"
  exit 1
fi

required_fields=(title slug date description categories tags keywords image)
errors=0
slugs_tmp="$(mktemp)"
cleanup() {
  rm -f "$slugs_tmp"
}
trap cleanup EXIT

for file in "$POSTS_DIR"/*.md; do
  [[ -e "$file" ]] || continue
  base="$(basename "$file")"

  # Section index is not a post article and can keep minimal metadata.
  if [[ "$base" == "_index.md" ]]; then
    continue
  fi

  delimiter_count=$(grep -c '^---' "$file" || true)
  if [[ "$delimiter_count" -lt 2 ]]; then
    echo "❌ $base: missing closing '---' front matter delimiter"
    errors=$((errors + 1))
  fi

  for field in "${required_fields[@]}"; do
    if ! grep -Eq "^${field}:" "$file"; then
      echo "❌ $base: missing required field '${field}'"
      errors=$((errors + 1))
    fi
  done

  # Validate title length
  title_line="$(grep -E '^title:' "$file" | head -n1 || true)"
  title="${title_line#title:}"
  title="$(printf '%s' "$title" | sed -E "s/^[[:space:]]+//; s/[[:space:]]+$//; s/^[\"']+//; s/[\"']+$//")"
  if [[ -z "$title" ]]; then
    echo "❌ $base: title must not be empty"
    errors=$((errors + 1))
  elif (( ${#title} < 10 )); then
    echo "❌ $base: title should be at least 10 characters"
    errors=$((errors + 1))
  fi

  slug_line="$(grep -E '^slug:' "$file" | head -n1 || true)"
  slug="${slug_line#slug:}"
  slug="$(printf '%s' "$slug" | sed -E "s/^[[:space:]]+//; s/[[:space:]]+$//; s/^[\"']+//; s/[\"']+$//")"

  if [[ -z "$slug" ]]; then
    echo "❌ $base: slug must not be empty"
    errors=$((errors + 1))
  elif [[ ! "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    echo "❌ $base: slug must use lowercase letters, digits, and hyphens only"
    errors=$((errors + 1))
  else
    if grep -q -F -x "$slug" "$slugs_tmp"; then
      echo "❌ $base: duplicate slug '$slug'"
      errors=$((errors + 1))
    else
      printf '%s\n' "$slug" >> "$slugs_tmp"
    fi
  fi

  description_line="$(grep -E '^description:' "$file" | head -n1 || true)"
  description="${description_line#description:}"
  description="$(printf '%s' "$description" | sed -E "s/^[[:space:]]+//; s/[[:space:]]+$//; s/^[\"']+//; s/[\"']+$//")"
  if [[ -z "$description" ]]; then
    echo "❌ $base: description must not be empty"
    errors=$((errors + 1))
  elif (( ${#description} < 100 )); then
    echo "❌ $base: description should be at least 100 characters for SEO snippet quality"
    errors=$((errors + 1))
  fi

  # Validate categories
  categories_line="$(grep -E '^categories:' "$file" | head -n1 || true)"
  categories="${categories_line#categories:}"
  if [[ -z "$categories" ]]; then
    echo "❌ $base: categories must not be empty"
    errors=$((errors + 1))
  fi

  date_line="$(grep -E '^date:' "$file" | head -n1 || true)"
  date_value="${date_line#date:}"
  date_value="$(printf '%s' "$date_value" | sed -E "s/^[[:space:]]+//; s/[[:space:]]+$//; s/^[\"']+//; s/[\"']+$//")"
  if [[ ! "$date_value" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "❌ $base: date must use YYYY-MM-DD format"
    errors=$((errors + 1))
  fi

  image_line="$(grep -E '^image:' "$file" | head -n1 || true)"
  image_value="${image_line#image:}"
  image_value="$(printf '%s' "$image_value" | sed -E "s/^[[:space:]]+//; s/[[:space:]]+$//; s/^[\"']+//; s/[\"']+$//")"
  if [[ -z "$image_value" ]]; then
    echo "❌ $base: image must not be empty"
    errors=$((errors + 1))
  elif [[ ! "$image_value" =~ ^/ && ! "$image_value" =~ ^https?:// ]]; then
    echo "❌ $base: image must be an absolute path (/...) or full URL"
    errors=$((errors + 1))
  fi

done

if (( errors > 0 )); then
  echo "❌ Front matter validation failed with $errors issue(s)."
  exit 1
fi

echo "✅ Front matter validation passed."
