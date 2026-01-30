#!/usr/bin/env python3
"""
Simple static site builder with zero external dependencies.
Builds HTML from markdown files in content/ directory.
"""

import re
import html
from pathlib import Path
from datetime import datetime
from config import SITE_TITLE, SITE_DESC, SITE_URL, POSTS_PER_PAGE, NAV_LINKS


# Directories
PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
OUTPUT_DIR = PROJECT_ROOT / "public"

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
    text = _convert_headers(text)
    text = _convert_emphasis(text)
    text = _convert_images(text)
    text = _convert_links(text)
    text = _convert_code(text)
    text = _convert_lists(text)
    text = _convert_blockquotes(text)
    text = _convert_paragraphs(text)
    return text


def _convert_headers(text):
    """Convert markdown headers to HTML."""
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    return text


def _convert_emphasis(text):
    """Convert markdown emphasis (bold/italic) to HTML."""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    return text


def _convert_images(text):
    """Convert markdown images to HTML."""
    return re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', text)


def _convert_links(text):
    """Convert markdown links to HTML."""
    return re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)


def _convert_code(text):
    """Convert markdown code blocks and inline code to HTML."""
    # Code blocks first (before inline code to avoid conflicts)
    text = re.sub(
        r'```[a-z]*\n(.*?)\n```',
        r'<pre><code>\1</code></pre>',
        text,
        flags=re.DOTALL
    )
    # Inline code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text


def _convert_lists(text):
    """Convert markdown lists to HTML."""
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
    return text


def _convert_blockquotes(text):
    """Convert markdown blockquotes to HTML."""
    return re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)


def _convert_paragraphs(text):
    """Convert markdown paragraphs to HTML."""
    paragraphs = text.split('\n\n')
    text = '\n\n'.join(
        f'<p>{p}</p>' if p and not p.startswith('<') else p
        for p in paragraphs
    )
    return text


def load_css():
    """Load CSS file.
    
    Returns:
        str: CSS content
    
    Raises:
        FileNotFoundError: If style.css does not exist
    """
    css_path = Path(__file__).parent / "style.css"
    if not css_path.exists():
        raise FileNotFoundError("❌ style.css not found - cannot build site")
    return css_path.read_text(encoding="utf-8")


def load_template():
    """Load HTML template.
    
    Returns:
        str: HTML template content
    
    Raises:
        FileNotFoundError: If template.html does not exist
    """
    template_path = Path(__file__).parent / "template.html"
    if not template_path.exists():
        raise FileNotFoundError("❌ template.html not found - cannot build site")
    return template_path.read_text(encoding="utf-8")


def render_html(title, content, description=None):
    """Render complete HTML page from template."""
    template = load_template()
    css = load_css()
    
    # Build navigation
    nav_html = '\n                '.join(
        f'<a href="{url}">{name}</a>' for name, url in NAV_LINKS
    )
    
    # Fill template
    html_output = template.replace("{{title}}", f"{title} - {SITE_TITLE}" if title != SITE_TITLE else title)
    html_output = html_output.replace("{{description}}", description or SITE_DESC)
    html_output = html_output.replace("{{site_title}}", SITE_TITLE)
    html_output = html_output.replace("{{site_desc}}", SITE_DESC)
    html_output = html_output.replace("{{navigation}}", nav_html)
    html_output = html_output.replace("{{content}}", content)
    html_output = html_output.replace("{{css}}", css)
    html_output = html_output.replace("{{year}}", str(datetime.now().year))
    
    return html_output


def get_posts():
    """Get all published blog posts, sorted by date (newest first)."""
    posts = []
    posts_dir = CONTENT_DIR / "posts"
    
    if not posts_dir.exists():
        return []
    
    for md_file in posts_dir.glob("*.md"):
        # Skip template
        if md_file.name.startswith("_"):
            continue
            
        meta, body = parse_markdown_file(md_file)
        
        # Validation - required fields
        if not meta.get("title"):
            print(f"⚠️  Warning: {md_file.name} missing 'title' - skipping")
            continue
        
        if not meta.get("date"):
            print(f"⚠️  Warning: {md_file.name} missing 'date' - skipping")
            continue
        
        # Skip drafts
        if meta.get("draft", "false").lower() == "true":
            continue
        
        # Parse date
        date = parse_date(meta.get("date"))
        if not date:
            print(f"⚠️  Warning: {md_file.name} invalid date format - skipping")
            continue
        
        # Parse updated date (optional)
        updated = parse_date(meta.get("updated")) or date
        
        posts.append({
            "title": meta.get("title"),
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
    """Build blog with pagination."""
    posts = get_posts()
    total_pages = (len(posts) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    
    (OUTPUT_DIR / "blog").mkdir(exist_ok=True)
    
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * POSTS_PER_PAGE
        end_idx = start_idx + POSTS_PER_PAGE
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
        
        description = f"Data engineering blog - Articles about ETL, Python, databases, and infrastructure. Page {page_num} of {total_pages}." if total_pages > 1 else "Data engineering blog - Articles about ETL, Python, databases, and infrastructure."
        html = render_html("Blog", content, description)
        
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
        
        description = post['description'] or f"{post['title']} - {SITE_DESC}"
        html = render_html(post['title'], content, description)
        post_dir = OUTPUT_DIR / "posts" / post['slug']
        post_dir.mkdir(exist_ok=True, parents=True)
        
        with open(post_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build_pages():
    """Build static pages (about, cv, contact)."""
    page_descriptions = {
        "about": "About Issa Sanogo - Data Engineer and open source advocate",
        "cv": "Resume of Issa Sanogo - Senior Data Engineer with 8+ years experience in data infrastructure and pipelines",
        "contact": "Contact Issa Sanogo - Get in touch via email, LinkedIn or GitHub"
    }
    
    for page_name in ["about", "cv", "contact"]:
        page_file = CONTENT_DIR / f"{page_name}.md"
        
        if not page_file.exists():
            continue
        
        meta, body = parse_markdown_file(page_file)
        title = meta.get("title", page_name.capitalize())
        description = page_descriptions.get(page_name, SITE_DESC)
        
        content = f"""
        <h1 class="page-title">{title}</h1>
        {markdown_to_html(body)}
        """
        
        html = render_html(title, content, description)
        page_dir = OUTPUT_DIR / page_name
        page_dir.mkdir(exist_ok=True)
        
        with open(page_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build_sitemap():
    """Build sitemap.xml for search engines."""
    posts = get_posts()
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Homepage
    sitemap += f'  <url>\n    <loc>{SITE_URL}/</loc>\n'
    sitemap += f'    <priority>1.0</priority>\n  </url>\n'
    
    # Blog
    sitemap += f'  <url>\n    <loc>{SITE_URL}/blog</loc>\n'
    sitemap += f'    <priority>0.9</priority>\n  </url>\n'
    
    # Static pages
    for page, priority in [("about", "0.8"), ("cv", "0.8"), ("contact", "0.7")]:
        sitemap += f'  <url>\n    <loc>{SITE_URL}/{page}</loc>\n'
        sitemap += f'    <priority>{priority}</priority>\n  </url>\n'
    
    # Blog posts
    for post in posts:
        sitemap += f'  <url>\n    <loc>{SITE_URL}/posts/{post["slug"]}</loc>\n'
        sitemap += f'    <lastmod>{post["updated"].strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap += f'    <priority>0.6</priority>\n  </url>\n'
    
    sitemap += '</urlset>'
    
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def build():
    """Build entire site.
    
    Returns:
        bool: True if build successful, False otherwise
    """
    # Pre-flight checks
    src_dir = Path(__file__).parent
    required_files = [
        (src_dir / "style.css", "CSS stylesheet"),
        (src_dir / "template.html", "HTML template"),
        (src_dir / "config.py", "Configuration"),
    ]
    
    missing = []
    for file_path, description in required_files:
        if not file_path.exists():
            missing.append(f"  • {file_path.name} ({description})")
    
    if missing:
        print("❌ Missing required files:")
        for item in missing:
            print(item)
        return False
    
    if not CONTENT_DIR.exists():
        print(f"❌ Content directory '{CONTENT_DIR}' not found")
        return False
    
    # Build site
    try:
        print("🔨 Building site...")
        build_home()
        build_blog()
        build_posts()
        build_pages()
        build_sitemap()
        print(f"✅ Site built successfully in {OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False


if __name__ == "__main__":
    build()
