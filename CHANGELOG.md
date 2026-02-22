# Changements — Zero-install & Reproductibilité 100%

**Date:** 22 février 2026
**Objectif:** Repo clean, cohérent, reproductible sans aucune installation macOS (sauf Docker Desktop)

## Changements appliqués

### 1. Infrastructure Docker complète

**Fichiers modifiés:**
- `Dockerfile` — ajout stage `lint` avec Python 3.12 + pre-commit
- `docker-compose.yml` — ajout service `lint` + volume cache pre-commit
- `.dockerignore` — nettoyage références `.venv/` et `node_modules/`

**Résultat:** Tous les workflows (dev, build, test, lint, prod) s'exécutent en conteneurs.

### 2. Dev Container (VS Code)

**Fichiers créés:**
- `.devcontainer/Dockerfile` — image Ubuntu 24.04 + Hugo + pre-commit + outillage complet
- `.devcontainer/devcontainer.json` — config VS Code avec Docker-outside-of-Docker + postCreateCommand

**Résultat:** Environnement de développement reproductible via "Reopen in Container".

### 3. Git Hooks versionné et portable

**Fichiers créés:**
- `.githooks/pre-commit` — hook intelligent qui détecte contexte (macOS → Docker, devcontainer → natif)

**Fichiers modifiés:**
- `Makefile` — ajout cible `hooks` + intégration dans `setup`

**Résultat:** `git commit` exécute pre-commit automatiquement depuis macOS (via Docker) ou devcontainer (natif).

### 4. CI/CD alignée sur Docker

**Fichiers modifiés:**
- `.github/workflows/deploy.yml` — job `lint` utilise `docker compose --profile lint` au lieu de `actions/setup-python`

**Résultat:** GitHub Actions utilise exactement le même workflow Docker que local/devcontainer.

### 5. Nettoyage et cohérence

**Fichiers supprimés:**
- `requirements.txt` — obsolète (pre-commit tourne en conteneur)

**Fichiers modifiés:**
- `.gitignore` — suppression `.venv/`, `__pycache__/`, `*.pyc`
- `.editorconfig` — ajustement CSS indent_size=4
- `.pre-commit-config.yaml` — ajout `editorconfig-checker` + exclusion `assets/css/`

**Résultat:** Repo propre, aucun fichier lié à installation Python locale.

### 6. Documentation

**Fichiers créés:**
- `ONBOARDING.md` — guide complet premier usage (devcontainer + macOS)
- `CHANGELOG.md` — ce fichier

**Fichiers modifiés:**
- `README.md` — ajout lien vers ONBOARDING.md, clarification requirements

**Résultat:** Parcours d'onboarding clair pour contributeurs.

### 7. Corrections de contenu

**Fichiers modifiés:**
- `content/_index.md` — correction indentation YAML (tabs → espaces)
- `layouts/index.html` — mise à jour CTA vers blog + consulting
- `layouts/partials/head.html` — ajout meta keywords
- `layouts/posts/single.html` — ajout CTA consulting en fin d'article

## Validation effectuée

```bash
✅ make setup
✅ make build
✅ make test
✅ make lint
✅ git commit (hook pre-commit exécuté via Docker)
✅ docker compose config (syntaxe valide)
```

## Workflow reproductible

### Depuis macOS (host)

```bash
git clone https://github.com/ngsanogo/ngsanogo.github.io.git
cd ngsanogo.github.io
make setup
make dev
# commit fonctionne via hook Docker
```

### Depuis Dev Container

```bash
# Ouvrir dans VS Code
code .
# Cmd+Shift+P > Dev Containers: Reopen in Container
make setup
make dev
# commit fonctionne via hook natif
```

### CI (GitHub Actions)

```yaml
- uses: actions/checkout@v4
- run: docker compose --profile lint run --rm lint
- run: docker compose --profile build run --rm build
```

## Images Docker construites

```
ngsanogogithubio-build:latest  (88.7MB) — Hugo Alpine
ngsanogogithubio-lint:latest   (237MB)  — Python 3.12 + pre-commit
ngsanogogithubio-test:latest   (88.7MB) — Hugo Alpine
ngsanogogithubio-prod:latest   (produit au besoin) — Nginx Alpine
```

## Prérequis stricts

- macOS avec Docker Desktop
- VS Code avec extension "Dev Containers" (optionnel mais recommandé)

**Aucune installation locale de Python, Hugo, Node.js, npm, pre-commit, etc.**

## Prochaines étapes recommandées

- [ ] Tester onboarding sur machine vierge (macOS fresh install)
- [ ] Documenter workflow création de post (`hugo new content/posts/...`)
- [ ] Ajouter commande `make new-post TITLE="..."` dans Makefile
- [ ] Configurer Dependabot pour mettre à jour pre-commit hooks

## Historique

- **22 février 2026** — Migration vers zero-install complet (Docker + devcontainer)
