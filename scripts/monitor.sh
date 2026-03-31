#!/usr/bin/env bash
# Script de monitoring des performances
set -euo pipefail

echo "📊 Monitoring site performance..."

# Vérifier la taille du site
site_size=$(du -sh public/ | cut -f1)
echo "Site size: $site_size"

# Vérifier les liens
echo "Checking links..."
docker run --rm --entrypoint sh -v "$PWD":/data lycheeverse/lychee:latest -lc 'find /data/public -name "*.html" -print0 | xargs -0 lychee --offline --no-progress --base-url /data/public --timeout 10 --max-concurrency 16 --threads 8 --'

# Vérifier la qualité du front matter
echo "Checking front matter quality..."
make test-content

echo "✅ Monitoring complete"
