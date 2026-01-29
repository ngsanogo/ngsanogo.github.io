#!/usr/bin/env python3
"""
Build statique minimaliste et zen pour ngsanogo.github.io
Suit la philosophie zen de Python : simple, lisible et beau
Zéro dépendances externes - utilise uniquement la stdlib
"""

import os
import re
import html
from pathlib import Path
from datetime import datetime

# Configuration
CONTENT_DIR = Path("content")
OUTPUT_DIR = Path("public")
SITE_TITLE = "Issa Sanogo"
SITE_DESC = "Senior Data Engineer"
SITE_URL = "https://ngsanogo.github.io"

# Crée le dossier de sortie
OUTPUT_DIR.mkdir(exist_ok=True)


def simple_markdown(text):
    """Parse minimaliste de markdown"""
    # Échappe le HTML
    text = html.escape(text)
    
    # Headers
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Bold et italic
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Liens
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Listes
    text = re.sub(r'^\* (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(?:<li>.*?</li>)', lambda m: '<ul>' + m.group(0) + '</ul>', text, flags=re.DOTALL)
    text = re.sub(r'</ul>\n<ul>', '', text)
    
    # Code inline
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    
    # Code blocks
    text = re.sub(r'```(.*?)\n(.*?)\n```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)
    
    # Paragraphes
    paragraphs = text.split('\n\n')
    text = '\n\n'.join(f'<p>{p}</p>' if p and not p.startswith('<') else p for p in paragraphs)
    
    # Blockquotes
    text = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    
    return text

# Configuration
CONTENT_DIR = Path("content")
OUTPUT_DIR = Path("public")
SITE_TITLE = "Issa Sanogo"
SITE_DESC = "Senior Data Engineer"
SITE_URL = "https://ngsanogo.github.io"

# Crée le dossier de sortie
OUTPUT_DIR.mkdir(exist_ok=True)


def read_markdown(file_path):
    """Lit un fichier markdown et retourne (frontmatter, contenu)"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse frontmatter (---\n...\n---)
    if content.startswith("---"):
        _, frontmatter, body = content.split("---\n", 2)
    else:
        frontmatter = ""
        body = content
    
    # Parse les variables du frontmatter
    meta = {}
    for line in frontmatter.strip().split("\n"):
        if ": " in line:
            key, value = line.split(": ", 1)
            meta[key.strip()] = value.strip('"').strip("'")
    
    return meta, body


def parse_date(date_str):
    """Parse une date au format YYYY-MM-DD"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None


def get_posts():
    """Récupère tous les posts triés par date (récent d'abord)"""
    posts = []
    posts_dir = CONTENT_DIR / "posts"
    
    if not posts_dir.exists():
        return posts
    
    for md_file in sorted(posts_dir.glob("*.md"), reverse=True):
        meta, body = read_markdown(md_file)
        
        # Skip les drafts
        if meta.get("draft", "false").lower() == "true":
            continue
        
        date = parse_date(meta.get("date", ""))
        if not date:
            continue
        
        posts.append({
            "title": meta.get("title", md_file.stem),
            "slug": meta.get("slug", md_file.stem),
            "date": date,
            "date_str": date.strftime("%B %d, %Y"),
            "description": meta.get("description", ""),
            "body": simple_markdown(body),
            "tags": meta.get("tags", "").split(", ") if meta.get("tags") else [],
        })
    
    return sorted(posts, key=lambda x: x["date"], reverse=True)


def get_page(slug):
    """Récupère une page (about, cv, contact)"""
    page_file = CONTENT_DIR / f"{slug}" / "index.md"
    
    if not page_file.exists():
        return None
    
    meta, body = read_markdown(page_file)
    return {
        "title": meta.get("title", slug.capitalize()),
        "slug": slug,
        "body": simple_markdown(body),
    }


def render_html(title, content, is_home=False):
    """Rend une page HTML complète"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {SITE_TITLE}</title>
    <meta name="description" content="{SITE_DESC}">
    <style>
        :root {{
            --primary: #1a1a1a;
            --secondary: #666;
            --accent: #0066cc;
            --light: #f5f5f5;
            --spacing: 1.5rem;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        html {{ font-size: 16px; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: var(--primary);
            background: white;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 720px;
            margin: 0 auto;
            padding: var(--spacing);
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
            border-bottom: 1px solid var(--light);
            padding-bottom: 2rem;
        }}
        
        .site-title {{
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 0.5rem;
        }}
        
        .site-title a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .site-title a:hover {{
            color: var(--accent);
        }}
        
        .site-desc {{
            color: var(--secondary);
            font-size: 1rem;
        }}
        
        nav {{
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }}
        
        nav a {{
            color: var(--secondary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}
        
        nav a:hover {{
            color: var(--accent);
        }}
        
        nav a.active {{
            color: var(--accent);
        }}
        
        main {{
            margin: 2rem 0;
        }}
        
        .page-title {{
            font-size: 1.8rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }}
        
        .post-item {{
            margin-bottom: 2.5rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--light);
        }}
        
        .post-item:last-child {{
            border-bottom: none;
        }}
        
        .post-title {{
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
        }}
        
        .post-title a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        .post-title a:hover {{
            color: var(--accent);
        }}
        
        .post-meta {{
            color: var(--secondary);
            font-size: 0.9rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        
        .post-description {{
            margin-top: 0.75rem;
            color: var(--primary);
        }}
        
        .post-tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 0.75rem;
        }}
        
        .tag {{
            background: var(--light);
            color: var(--secondary);
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.85rem;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            font-weight: 700;
        }}
        
        h1 {{ font-size: 2rem; }}
        h2 {{ font-size: 1.5rem; }}
        h3 {{ font-size: 1.25rem; }}
        
        p {{ margin-bottom: 1rem; }}
        
        ul, ol {{
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        li {{ margin-bottom: 0.5rem; }}
        
        a {{
            color: var(--accent);
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        code {{
            background: var(--light);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.9rem;
        }}
        
        pre {{
            background: var(--light);
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 1rem;
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        blockquote {{
            border-left: 4px solid var(--accent);
            padding-left: 1rem;
            color: var(--secondary);
            margin: 1.5rem 0;
        }}
        
        footer {{
            text-align: center;
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px solid var(--light);
            color: var(--secondary);
            font-size: 0.9rem;
        }}
        
        .read-more {{
            color: var(--accent);
            font-weight: 500;
            display: inline-block;
            margin-top: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1 class="site-title"><a href="/">{SITE_TITLE}</a></h1>
            <p class="site-desc">{SITE_DESC}</p>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/blog">Blog</a>
                <a href="/cv">Resume</a>
                <a href="/contact">Contact</a>
            </nav>
        </header>
        
        <main>
            {content}
        </main>
        
        <footer>
            <p>&copy; 2024 {SITE_TITLE}. Built with Python.</p>
        </footer>
    </div>
</body>
</html>
"""


def build_index():
    """Génère la page d'accueil"""
    posts = get_posts()
    
    posts_html = ""
    for post in posts[:5]:  # Derniers 5 posts
        posts_html += f"""
        <div class="post-item">
            <h2 class="post-title"><a href="/posts/{post['slug']}">{post['title']}</a></h2>
            <div class="post-meta">
                <span>{post['date_str']}</span>
            </div>
            <p class="post-description">{post['description']}</p>
            <a href="/posts/{post['slug']}" class="read-more">Read more →</a>
        </div>
        """
    
    if posts:
        posts_html += f'<p style="text-align: center; margin-top: 2rem;"><a href="/blog">View all {len(posts)} posts →</a></p>'
    
    content = f"""
        <h1 class="page-title">Welcome</h1>
        <p>Data Engineer with expertise in building data infrastructure, pipelines, and analytics solutions.</p>
        <h2 style="margin-top: 2rem;">Latest Posts</h2>
        {posts_html}
    """
    
    html = render_html(SITE_TITLE, content, is_home=True)
    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def build_blog():
    """Génère la page du blog avec tous les posts"""
    posts = get_posts()
    
    posts_html = ""
    for post in posts:
        posts_html += f"""
        <div class="post-item">
            <h2 class="post-title"><a href="/posts/{post['slug']}">{post['title']}</a></h2>
            <div class="post-meta">
                <span>{post['date_str']}</span>
            </div>
            <p class="post-description">{post['description']}</p>
            <a href="/posts/{post['slug']}" class="read-more">Read more →</a>
        </div>
        """
    
    content = f"""
        <h1 class="page-title">Blog</h1>
        <p>All posts about data engineering, tools, and best practices.</p>
        {posts_html}
    """
    
    html = render_html("Blog", content)
    (OUTPUT_DIR / "blog").mkdir(exist_ok=True)
    with open(OUTPUT_DIR / "blog" / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def build_posts():
    """Génère une page pour chaque post"""
    posts = get_posts()
    
    (OUTPUT_DIR / "posts").mkdir(exist_ok=True)
    
    for post in posts:
        content = f"""
        <h1 class="page-title">{post['title']}</h1>
        <div class="post-meta">
            <span>{post['date_str']}</span>
        </div>
        {post['body']}
        """
        
        html = render_html(post['title'], content)
        post_dir = OUTPUT_DIR / "posts" / post['slug']
        post_dir.mkdir(exist_ok=True, parents=True)
        with open(post_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build_pages():
    """Génère les pages statiques (about, cv, contact)"""
    for slug in ["about", "cv", "contact"]:
        page = get_page(slug)
        if not page:
            continue
        
        content = f"""
        <h1 class="page-title">{page['title']}</h1>
        {page['body']}
        """
        
        html = render_html(page['title'], content)
        page_dir = OUTPUT_DIR / slug
        page_dir.mkdir(exist_ok=True)
        with open(page_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build():
    """Construit le site complet"""
    print("🔨 Building site...")
    build_index()
    build_blog()
    build_posts()
    build_pages()
    print(f"✅ Site built in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()
