# Issa Sanogo

This is my personal website where I share articles about data engineering, programming, and tech topics.

## About This Site

I write about:
- **Data Engineering** - ETL, orchestration, databases
- **Programming** - Python, R, Git, Linux fundamentals
- **Tools & Infrastructure** - Docker, Multipass, PostgreSQL, Apache Airflow

The site is built from plain markdown files and automatically published whenever I push changes.

## How It Works

```
src/
├── build.py         # Generates the website
├── config.py        # Site configuration
├── template.html    # HTML structure
├── style.css        # Styling
└── dev.py          # Local preview server

content/
├── posts/           # My articles
├── about.md        # About me
├── cv.md           # My resume
└── contact.md      # How to reach me

tests/
└── test_build.py   # Unit tests
```

## Adding an Article

**Use the template:**

```bash
cp content/posts/_template.md content/posts/my-article.md
# Edit the file, change draft to false
python3 src/build.py
```

**Or create manually** - `content/posts/my-article.md`:

```markdown
---
title: My Article Title
slug: my-article
date: 2024-01-30
description: Brief summary for the listing
draft: false
---

# Article content here

Write in markdown with **bold**, *italic*, [links](url), etc.
```

Optional: Add `updated: 2024-02-01` to mark an article as recently updated.

## Editing Pages

Edit `about.md`, `cv.md`, or `contact.md` directly. Just need a title at the top:

```markdown
---
title: About Me
---

Your content...
```

## Building & Deploying

**Local build:**
```bash
python3 src/build.py
```

**Local preview:**
```bash
python3 src/dev.py
# Visit http://localhost:8000
```

**Run tests:**
```bash
python3 -m unittest discover tests/ -v
```

The site automatically builds and deploys to GitHub Pages when you push to main.

```bash
python3 build.py
```

Push to GitHub → automatically deployed via GitHub Actions.
