# Architecture du Site

## Vue d'Ensemble

Site statique généré en Python avec **zéro dépendance externe**.

**Stack :**
- Python 3.11+ (stdlib uniquement)
- Markdown → HTML
- GitHub Actions → GitHub Pages

**Philosophie :**
- Simple > Complexe
- Explicite > Implicite
- Lisible > Clever
- Maintenable > Feature-rich

## Structure Projet

```
ngsanogo.github.io/
├── src/                      # Code source
│   ├── build.py             # Générateur site
│   ├── config.py            # Configuration centralisée
│   ├── template.html        # Structure HTML
│   ├── style.css            # Styles CSS
│   ├── dev.py               # Serveur développement
│   └── static/              # Fichiers statiques
│       ├── robots.txt       # Instructions crawlers
│       ├── 404.html         # Page erreur
│       └── favicon.svg      # Favicon
│
├── content/                  # Contenu markdown
│   ├── posts/               # Articles blog
│   │   ├── _template.md    # Template nouvel article
│   │   └── *.md            # Articles (13 actuels)
│   ├── about.md            # Page À propos
│   ├── cv.md               # CV/Resume
│   ├── contact.md          # Contact
│   └── projects.md         # Projets
│
├── tests/                    # Tests unitaires
│   └── test_build.py        # 37 tests (100% passing)
│
├── public/                   # Sortie générée (gitignored)
│   ├── index.html
│   ├── blog/               # Pages blog paginées
│   ├── posts/              # Articles individuels
│   ├── sitemap.xml
│   ├── robots.txt
│   ├── 404.html
│   └── favicon.svg
│
├── .github/workflows/
│   └── deploy.yml           # CI/CD (test → build → deploy)
│
├── Makefile                 # Commandes développement
├── .editorconfig            # Cohérence code
└── README.md                # Documentation
```

## Flux de Build

```
1. Config (config.py)
   ↓
2. Parse Markdown (content/*.md)
   ↓ _parse_post_file(), _validate_post_meta()
   ↓
3. Convert to HTML (markdown_to_html)
   ↓ 8 conversion functions
   ↓
4. Render Pages (template.html + content)
   ↓ render_html(), render_post_item(), render_pagination()
   ↓
5. Write Files (public/)
   ↓ build_home(), build_blog(), build_posts(), build_pages()
   ↓
6. Generate Sitemap (sitemap.xml)
   ↓ build_sitemap()
   ↓
7. Output (public/)
```

## Fonctions Clés

### Parsing (build.py)
- `parse_markdown_file()` - YAML frontmatter + body
- `_validate_post_meta()` - Validation metadata
- `_parse_post_file()` - Parse fichier complet
- `get_posts()` - Tous les posts publiés

### Markdown (build.py)
- `markdown_to_html()` - Orchestration conversion
- `_convert_headers()` - h1/h2/h3
- `_convert_emphasis()` - bold/italic
- `_convert_links()` - liens
- `_convert_images()` - images
- `_convert_code()` - code inline/blocks
- `_convert_lists()` - listes
- `_convert_blockquotes()` - citations

### Templates (build.py)
- `render_html()` - Page HTML complète
- `render_post_item()` - Item article (réutilisable)
- `render_pagination()` - Navigation pages

### Build (build.py)
- `build_home()` - Homepage
- `build_blog()` - Blog paginé (10 posts/page)
- `build_posts()` - Articles individuels
- `build_pages()` - Pages statiques
- `build_sitemap()` - Sitemap XML
- `build()` - Orchestration complète

## Configuration (config.py)

```python
# Site
SITE_TITLE = "Issa Sanogo"
SITE_DESC = "Senior Data Engineer"
SITE_URL = "https://ngsanogo.github.io"

# Build
POSTS_PER_PAGE = 10
DATE_FORMAT = "%B %d, %Y"

# Navigation
NAV_LINKS = [("Home", "/"), ("Blog", "/blog"), ...]

# Sitemap
SITEMAP_PRIORITIES = {"home": 1.0, "blog": 0.9, ...}

# Dev server
DEV_SERVER_HOST = "localhost"
DEV_SERVER_PORT = 8000
```

## Tests (tests/test_build.py)

**37 tests organisés en 7 suites :**

1. **TestMarkdownParsing** - Conversion markdown
2. **TestFrontmatterParsing** - YAML parsing
3. **TestTemplateRendering** - Templates HTML
4. **TestBuildHelpers** - Fonctions helper
5. **TestBuildIntegration** - Build complet
6. **TestEdgeCases** - Cas limites
7. **TestSEOFeatures** - SEO (Schema.org, Open Graph, canonical)
8. **TestSiteStructure** - Vérification fichiers

**Coverage : ~85%**

## Commandes Développement

```bash
make build    # Build site
make test     # Run tests
make dev      # Build + serveur local (localhost:8000)
make clean    # Nettoyer fichiers générés
make all      # Clean + test + build
```

## Conventions

### Frontmatter Articles
```yaml
---
title: "Titre Article"      # Requis
slug: article-slug          # Requis
date: YYYY-MM-DD           # Requis
description: "Description" # Requis
draft: false               # Requis (true = ignoré)
updated: YYYY-MM-DD       # Optionnel
---
```

### Frontmatter Pages
```yaml
---
title: "Titre Page"  # Suffisant
---
```

### URLs Générées
- Homepage : `/`
- Blog : `/blog`, `/blog/page/2`, ...
- Post : `/posts/{slug}/`
- Page : `/{page_name}/`

## Extension

### Ajouter Nouveau Type Page

```python
# src/build.py
def build_xyz():
    """Build XYZ pages."""
    xyz_dir = CONTENT_DIR / "xyz"
    if not xyz_dir.exists():
        return
    
    for file in xyz_dir.glob("*.md"):
        meta, body = parse_markdown_file(file)
        content = f"<h1>{meta['title']}</h1>{markdown_to_html(body)}"
        html = render_html(meta['title'], content)
        # Write...

# Dans build()
def build():
    build_home()
    build_blog()
    build_posts()
    build_pages()
    build_xyz()  # Nouveau
```

### Étendre Parser Markdown

```python
# src/build.py
def _convert_xyz(text):
    """Convert XYZ syntax."""
    return re.sub(pattern, replacement, text)

def markdown_to_html(text):
    text = _convert_headers(text)
    # ...
    text = _convert_xyz(text)  # Nouveau
    text = _convert_paragraphs(text)
    return text
```

### Modifier Configuration

```python
# src/config.py
NEW_SETTING = "value"

# src/build.py
from config import ..., NEW_SETTING

# Utiliser NEW_SETTING dans le code
```

## CI/CD Pipeline

**GitHub Actions (.github/workflows/deploy.yml) :**

```
1. TEST
   - python3 -m unittest discover tests/
   - ❌ Si échec → stop

2. BUILD
   - python3 src/build.py
   - Validate sitemap.xml + index.html
   - ❌ Si échec → stop

3. DEPLOY
   - Upload public/ → GitHub Pages
   - ✅ Site live
```

## Dépendances

**Zero externes - Python stdlib uniquement :**
- `pathlib` - Chemins
- `datetime` - Dates
- `re` - Regex markdown
- `html` - Escape
- `logging` - Logs structurés
- `http.server` - Serveur dev
- `unittest` - Tests

**Pourquoi zéro dépendances ?**
- Simplicité
- Sécurité (pas de CVE externes)
- Durabilité (pas de breaking changes)
- Portabilité (run partout)

## Métriques

**Code :**
- 990 lignes Python total
- 592 lignes build.py
- 305 lignes tests
- 27 fonctions (avg 17 lignes)
- 23 tests (100% passing)

**Performance :**
- Build < 1s (13 posts)
- Scalable jusqu'à ~50 posts

## Troubleshooting

**Build échoue**
```bash
# Vérifier fichiers requis
make build  # Messages d'erreur clairs

# Logs détaillés dans console
# Timestamps + niveaux (INFO/WARNING/ERROR)
```

**Tests échouent**
```bash
make test  # Voir détails

# Test spécifique
python3 -m unittest tests.test_build.TestClassName.test_name -v
```

**Serveur dev ne démarre pas**
```bash
# Port 8000 occupé ?
# Modifier DEV_SERVER_PORT dans src/config.py
```

**Articles ne s'affichent pas**
- Vérifier `draft: false`
- Vérifier format date (YYYY-MM-DD)
- Consulter logs build (warnings)

## Maintenance

### Ajouter Article
```bash
cp content/posts/_template.md content/posts/nouveau.md
# Éditer, mettre draft: false
make build
git add . && git commit -m "Add: nouveau article" && git push
```

### Mettre à Jour CV
```bash
vim content/cv.md
make build && make dev  # Preview
git push
```

### Changer Style
```bash
vim src/style.css
make build && make dev
git push
```

## Roadmap (Optionnel)

**Si besoin futur :**
- Type hints (mypy)
- Validation accessibilité (a11y)
- RSS feed
- Tags/categories
- Search
- Comments (via service externe)

**Non prévu :**
- Base de données
- Backend dynamique
- CMS
- Dépendances externes
