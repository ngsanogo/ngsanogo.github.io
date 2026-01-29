# Mon Site - Python Zen Edition

Un site simple, beau et facile à maintenir. Construit avec Python suivant la philosophie Zen.

## 🚀 Démarrage rapide

### Ajouter un article de blog

```bash
# Créer un nouveau fichier dans content/posts/
touch content/posts/mon-article.md
```

Remplissez avec ce template:

```markdown
---
title: Mon Super Article
slug: mon-article
date: 2024-01-29
description: Une courte description de l'article
tags: python, data, engineering
draft: false
---

# Mon Article

Votre contenu ici...
```

### Modifier vos pages

Les pages principales (About, CV, Contact) sont dans `content/`:

- `content/about/index.md` - Page À propos
- `content/cv/index.md` - Votre CV / Resume
- `content/contact/index.md` - Contact

### Builder le site

```bash
python3 build.py
```

Le site sera généré dans `public/`.

## 📝 Format Markdown supporté

- `# Titres` (h1, h2, h3)
- `**gras**` et `*italique*`
- `[lien](url)`
- `` `code inline` ``
- Code blocks avec ```
- Listes avec `*`
- Blockquotes avec `>`

## 🎨 Personnaliser le design

Le CSS est embarqué dans `build.py`. Vous pouvez:

1. Changer les couleurs dans `:root { --primary: #xxx; }`
2. Modifier la typographie
3. Ajouter des sections

Tout est en Python - pas de dépendances externes!

## 📋 Structure du projet

```
.
├── build.py              # Le générateur (tout est ici!)
├── content/
│   ├── about/index.md
│   ├── cv/index.md
│   ├── contact/index.md
│   └── posts/            # Vos articles
├── public/               # Généré (ne pas modifier)
└── .github/workflows/    # GitHub Actions
```

## ✅ Ce qui marche

- ✅ Articles de blog simples
- ✅ Pages statiques  
- ✅ Responsive design
- ✅ SEO-friendly
- ✅ Zéro dépendances externes
- ✅ Déploiement automatique sur GitHub Pages

## 🎯 Philosophie Zen

Ce site suit les principes zen de Python:
- **Simple > Complexe** - Python pur, pas de frameworks lourds
- **Beau > Laid** - Design minimaliste et élégant
- **Lisible > Obscur** - Code facile à comprendre et modifier

Bienvenue dans la simplicité! 🚀
