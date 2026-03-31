#!/usr/bin/env bash
# Test unitaire pour la validation front matter
set -euo pipefail

echo "🧪 Running front matter validation tests..."

# Test de validation de slug valide
echo "Testing valid slug..."
echo "title: Test Post" > /tmp/test-valid.md
echo "slug: test-post" >> /tmp/test-valid.md
echo "date: 2023-01-01" >> /tmp/test-valid.md
echo "description: Test description with enough characters for validation" >> /tmp/test-valid.md
echo "categories: [\"data-engineering\"]" >> /tmp/test-valid.md
echo "tags: [\"test\"]" >> /tmp/test-valid.md
echo "keywords: []" >> /tmp/test-valid.md
echo "image: /images/test.jpg" >> /tmp/test-valid.md
echo "---" >> /tmp/test-valid.md
echo "Content" >> /tmp/test-valid.md

# Exécuter la validation
if ./scripts/validate-frontmatter.sh; then
  echo "✅ Valid slug test passed"
else
  echo "❌ Valid slug test failed"
fi

# Test de validation de slug invalide
echo "Testing invalid slug..."
echo "title: Test Post" > /tmp/test-invalid.md
echo "slug: Test-Post" >> /tmp/test-invalid.md  # Slug avec majuscule
echo "date: 2023-01-01" >> /tmp/test-invalid.md
echo "description: Test description with enough characters for validation" >> /tmp/test-invalid.md
echo "categories: [\"data-engineering\"]" >> /tmp/test-invalid.md
echo "tags: [\"test\"]" >> /tmp/test-invalid.md
echo "keywords: []" >> /tmp/test-invalid.md
echo "image: /images/test.jpg" >> /tmp/test-invalid.md
echo "---" >> /tmp/test-invalid.md
echo "Content" >> /tmp/test-invalid.md

# Exécuter la validation
if ! ./scripts/validate-frontmatter.sh; then
  echo "✅ Invalid slug test passed (correctly rejected)"
else
  echo "❌ Invalid slug test failed (should have been rejected)"
fi

# Test de validation de titre trop court
echo "Testing short title..."
echo "title: T" > /tmp/test-short-title.md
echo "slug: test-short-title" >> /tmp/test-short-title.md
echo "date: 2023-01-01" >> /tmp/test-short-title.md
echo "description: Test description with enough characters for validation" >> /tmp/test-short-title.md
echo "categories: [\"data-engineering\"]" >> /tmp/test-short-title.md
echo "tags: [\"test\"]" >> /tmp/test-short-title.md
echo "keywords: []" >> /tmp/test-short-title.md
echo "image: /images/test.jpg" >> /tmp/test-short-title.md
echo "---" >> /tmp/test-short-title.md
echo "Content" >> /tmp/test-short-title.md

# Exécuter la validation
if ! ./scripts/validate-frontmatter.sh; then
  echo "✅ Short title test passed (correctly rejected)"
else
  echo "❌ Short title test failed (should have been rejected)"
fi

# Nettoyage
rm -f /tmp/test-valid.md /tmp/test-invalid.md /tmp/test-short-title.md

echo "✅ All tests completed"
