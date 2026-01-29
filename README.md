# Issa Sanogo - Personal Site

A simple, fast, and easy-to-maintain personal website built with Python.

## 🎯 Structure

```
.
├── content/
│   ├── about.md          # About page
│   ├── cv.md             # Resume/CV
│   ├── contact.md        # Contact page
│   └── posts/            # Blog articles
├── build.py              # Site generator (no dependencies)
├── style.css             # Styling
└── public/               # Generated HTML (build output)
```

## ✍️ Add a Blog Post

Create a new file in `content/posts/`:

```bash
touch content/posts/my-article.md
```

Fill with this template:

```markdown
---
title: My Article Title
slug: my-article
date: 2024-01-30
description: Short description for listing
draft: false
---

# Your content here

Use markdown: **bold**, *italic*, [links](url), etc.
```

**Fields explained:**
- `title`: Article title (shown on page and listings)
- `slug`: URL path (e.g., `/posts/my-article`)
- `date`: Publication date (YYYY-MM-DD)
- `description`: Short preview text
- `draft`: Set to `true` to hide article
- `updated` (optional): Set to mark as recently updated

## 📄 Edit Pages

Pages are plain markdown files in `content/`:

- `about.md` → `/about`
- `cv.md` → `/cv`
- `contact.md` → `/contact`

Only required field: `title`

```markdown
---
title: Page Title
---

Your content here...
```

## 🏗️ Build

```bash
python3 build.py
```

Generates `public/` with complete site.

## 🎨 Customize

Edit `style.css` to change colors, fonts, or layout. Everything else is in `build.py` and is straightforward Python.

## 📋 Features

- **Zero dependencies** - Pure Python stdlib
- **Fast** - Static HTML generation
- **Simple** - No config, one way to do things
- **Maintainable** - All code is clear and readable
- **Blog pagination** - 10 posts per page
- **Latest posts** - Home shows newest + recently updated

## 🚀 Deploy

Push to GitHub. GitHub Actions automatically builds and deploys to Pages.
