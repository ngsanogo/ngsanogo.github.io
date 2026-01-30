#!/usr/bin/env python3
"""
Simple static site builder with zero external dependencies.
Builds HTML from markdown files in content/ directory.
"""

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

OUTPUT_DIR.mkdir(exist_ok=True)


def parse_markdown_file(file_path):
    """Parse markdown file with YAML frontmatter.
    
    Returns: (metadata_dict, body_text)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract frontmatter
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---\n", 2)
    if len(parts) != 3:
        return {}, content
    
    _, frontmatter, body = parts
    
    # Parse YAML-like frontmatter (simple key: value format)
    meta = {}
    for line in frontmatter.strip().split("\n"):
        if ": " in line:
            key, value = line.split(": ", 1)
            meta[key.strip()] = value.strip('" \'')
    
    return meta, body.strip()


def parse_date(date_str):
    """Parse YYYY-MM-DD date format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def markdown_to_html(text):
    """Convert markdown to HTML. Minimal but practical."""
    text = html.escape(text)
    
    # Headers
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Emphasis
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    
    # Images
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', text)
    
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    text = re.sub(
        r'```(.*?)\n(.*?)\n```',
        r'<pre><code>\2</code></pre>',
        text,
        flags=re.DOTALL
    )
    
    # Unordered lists
    text = re.sub(r'^\* (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
    # Numbered lists
    text = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
    # Wrap consecutive <li> in <ul>
    text = re.sub(
        r'((?:<li>.*?</li>\n?)+)',
        lambda m: '<ul>' + m.group(0) + '</ul>',
        text,
        flags=re.DOTALL
    )
    text = re.sub(r'</ul>\n<ul>', '', text)
    
    # Blockquotes
    text = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    
    # Paragraphs
    paragraphs = text.split('\n\n')
    text = '\n\n'.join(
        f'<p>{p}</p>' if p and not p.startswith('<') else p
        for p in paragraphs
    )
    
    return text


def load_css():
    """Load CSS file."""
    with open("style.css", "r", encoding="utf-8") as f:
        return f.read()


def render_html(title, content):
    """Render complete HTML page."""
    css = load_css()
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {SITE_TITLE}</title>
    <meta name="description" content="{SITE_DESC}">
    <style>{css}</style>
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
        <main>{content}</main>
        <footer>
            <p>&copy; {datetime.now().year} {SITE_TITLE}</p>
        </footer>
    </div>
</body>
</html>"""


def get_posts():
    """Get all published blog posts, sorted by date (newest first)."""
    posts = []
    posts_dir = CONTENT_DIR / "posts"
    
    if not posts_dir.exists():
        return []
    
    for md_file in posts_dir.glob("*.md"):
        meta, body = parse_markdown_file(md_file)
        
        # Skip drafts
        if meta.get("draft", "false").lower() == "true":
            continue
        
        # Parse date
        date = parse_date(meta.get("date"))
        if not date:
            continue
        
        # Parse updated date (optional)
        updated = parse_date(meta.get("updated")) or date
        
        posts.append({
            "title": meta.get("title", md_file.stem),
            "slug": meta.get("slug", md_file.stem),
            "date": date,
            "updated": updated,
            "date_str": date.strftime("%B %d, %Y"),
            "updated_str": updated.strftime("%B %d, %Y") if updated != date else None,
            "description": meta.get("description", ""),
            "body": markdown_to_html(body),
        })
    
    return sorted(posts, key=lambda x: x["date"], reverse=True)


def build_home():
    """Build homepage."""
    posts = get_posts()
    
    if not posts:
        content = """
        <h1 class="page-title">Welcome</h1>
        <p>Data Engineer with expertise in building data infrastructure, pipelines, and analytics solutions.</p>
        """
    else:
        latest_created = posts[0]
        posts_by_updated = sorted(posts, key=lambda x: x["updated"], reverse=True)
        latest_updated = posts_by_updated[0]
        
        posts_html = f"""
        <section class="home-section">
            <h2 class="section-title">📝 Latest Post</h2>
            <div class="post-item">
                <h2 class="post-title"><a href="/posts/{latest_created['slug']}">{latest_created['title']}</a></h2>
                <div class="post-meta"><span>Published: {latest_created['date_str']}</span></div>
                <p class="post-description">{latest_created['description']}</p>
                <a href="/posts/{latest_created['slug']}" class="read-more">Read more →</a>
            </div>
        </section>
        """
        
        if latest_updated['slug'] != latest_created['slug']:
            posts_html += f"""
        <section class="home-section">
            <h2 class="section-title">🔄 Recently Updated</h2>
            <div class="post-item">
                <h2 class="post-title"><a href="/posts/{latest_updated['slug']}">{latest_updated['title']}</a></h2>
                <div class="post-meta"><span>Updated: {latest_updated['updated_str'] or latest_updated['date_str']}</span></div>
                <p class="post-description">{latest_updated['description']}</p>
                <a href="/posts/{latest_updated['slug']}" class="read-more">Read more →</a>
            </div>
        </section>
            """
        
        posts_html += f'<p class="view-all"><a href="/blog" class="read-more">View all {len(posts)} posts →</a></p>'
        
        content = f"""
        <h1 class="page-title">Welcome</h1>
        <p>Data Engineer with expertise in building data infrastructure, pipelines, and analytics solutions.</p>
        {posts_html}
        """
    
    html = render_html(SITE_TITLE, content)
    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def build_blog():
    """Build blog with pagination (10 posts per page)."""
    posts = get_posts()
    posts_per_page = 10
    total_pages = (len(posts) + posts_per_page - 1) // posts_per_page
    
    (OUTPUT_DIR / "blog").mkdir(exist_ok=True)
    
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * posts_per_page
        end_idx = start_idx + posts_per_page
        page_posts = posts[start_idx:end_idx]
        
        posts_html = ""
        for post in page_posts:
            posts_html += f"""
            <div class="post-item">
                <h2 class="post-title"><a href="/posts/{post['slug']}">{post['title']}</a></h2>
                <div class="post-meta"><span>{post['date_str']}</span></div>
                <p class="post-description">{post['description']}</p>
                <a href="/posts/{post['slug']}" class="read-more">Read more →</a>
            </div>
            """
        
        # Pagination
        pagination_html = ""
        if total_pages > 1:
            pagination_html = '<div class="pagination">'
            
            # Previous button
            if page_num > 1:
                prev_url = "/blog" if page_num == 2 else f"/blog/page/{page_num - 1}"
                pagination_html += f'<a href="{prev_url}" class="read-more">← Previous</a>'
            else:
                pagination_html += '<span></span>'
            
            # Page numbers
            page_numbers = '<div class="page-numbers">'
            for i in range(1, total_pages + 1):
                page_url = "/blog" if i == 1 else f"/blog/page/{i}"
                if i == page_num:
                    page_numbers += f'<span>{i}</span>'
                else:
                    page_numbers += f'<a href="{page_url}">{i}</a>'
            page_numbers += '</div>'
            pagination_html += page_numbers
            
            # Next button
            if page_num < total_pages:
                pagination_html += f'<a href="/blog/page/{page_num + 1}" class="read-more">Next →</a>'
            else:
                pagination_html += '<span></span>'
            
            pagination_html += '</div>'
        
        page_info = f" (Page {page_num} of {total_pages})" if total_pages > 1 else ""
        content = f"""
            <h1 class="page-title">Blog</h1>
            <p>All posts about data engineering, tools, and best practices.{page_info}</p>
            {posts_html}
            {pagination_html}
        """
        
        html = render_html("Blog", content)
        
        if page_num == 1:
            with open(OUTPUT_DIR / "blog" / "index.html", "w", encoding="utf-8") as f:
                f.write(html)
        else:
            page_dir = OUTPUT_DIR / "blog" / "page" / str(page_num)
            page_dir.mkdir(exist_ok=True, parents=True)
            with open(page_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(html)


def build_posts():
    """Build individual blog post pages."""
    posts = get_posts()
    (OUTPUT_DIR / "posts").mkdir(exist_ok=True)
    
    for post in posts:
        content = f"""
        <h1 class="page-title">{post['title']}</h1>
        <div class="post-meta"><span>{post['date_str']}</span></div>
        {post['body']}
        """
        
        html = render_html(post['title'], content)
        post_dir = OUTPUT_DIR / "posts" / post['slug']
        post_dir.mkdir(exist_ok=True, parents=True)
        
        with open(post_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build_pages():
    """Build static pages (about, cv, contact)."""
    for page_name in ["about", "cv", "contact"]:
        page_file = CONTENT_DIR / f"{page_name}.md"
        
        if not page_file.exists():
            continue
        
        meta, body = parse_markdown_file(page_file)
        title = meta.get("title", page_name.capitalize())
        content = f"""
        <h1 class="page-title">{title}</h1>
        {markdown_to_html(body)}
        """
        
        html = render_html(title, content)
        page_dir = OUTPUT_DIR / page_name
        page_dir.mkdir(exist_ok=True)
        
        with open(page_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build():
    """Build entire site."""
    print("🔨 Building site...")
    build_home()
    build_blog()
    build_posts()
    build_pages()
    print(f"✅ Site built in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()
