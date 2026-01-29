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
content/
├── posts/           # My articles
├── about.md        # About me
├── cv.md           # My resume
└── contact.md      # How to reach me

build.py            # Generates the website
style.css           # Styling
```

## Adding an Article

Create `content/posts/my-article.md`:

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

```bash
python3 build.py
```

Push to GitHub → automatically deployed via GitHub Actions.
