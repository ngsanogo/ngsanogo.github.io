#!/usr/bin/env python3
"""
Simple static site builder with zero external dependencies.
Builds HTML from markdown files in content/ directory.
"""

import html
import json
import logging
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from config import (
    DATE_FORMAT,
    NAV_LINKS,
    POSTS_PER_PAGE,
    SITE_DESC,
    SITE_TITLE,
    SITE_URL,
    SITEMAP_PRIORITIES,
    STATIC_PAGES,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Directories
PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
OUTPUT_DIR = PROJECT_ROOT / "public"

OUTPUT_DIR.mkdir(exist_ok=True)

# Cache for template and CSS (one read per process; avoids repeated I/O during build)
_cached_template = None
_cached_css = None


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
    # Extract HTML blocks to preserve them (avoid escaping intentional HTML)
    html_blocks = []
    def save_html(match):
        html_blocks.append(match.group(0))
        return f"HTMLBLOCK{len(html_blocks) - 1}PLACEHOLDER"
    
    # Match HTML blocks (opening tag to closing tag)
    text = re.sub(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>.*?</\1>', save_html, text, flags=re.DOTALL)
    
    # Now escape remaining text
    text = html.escape(text)
    
    # Convert markdown
    text = _convert_horizontal_rules(text)
    text = _convert_headers(text)
    text = _convert_emphasis(text)
    text = _convert_images(text)
    text = _convert_links(text)
    text = _convert_code(text)
    text = _convert_lists(text)
    text = _convert_blockquotes(text)
    text = _convert_paragraphs(text)
    
    # Restore HTML blocks
    for i, block in enumerate(html_blocks):
        text = text.replace(f"HTMLBLOCK{i}PLACEHOLDER", block)
    
    return text


def _convert_horizontal_rules(text):
    """Convert markdown horizontal rules to HTML."""
    return re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)


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
    """Convert markdown images to HTML with lazy loading."""
    return re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" loading="lazy">', text)


def _convert_links(text):
    """Convert markdown links to HTML. External links get rel='noopener noreferrer'."""
    def repl(m):
        label, url = m.group(1), m.group(2)
        attrs = ' rel="noopener noreferrer"' if url.startswith(('http://', 'https://')) else ''
        return f'<a href="{url}"{attrs}>{label}</a>'
    return re.sub(r'\[(.*?)\]\((.*?)\)', repl, text)


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
        f'<p>{p}</p>' if p and not p.startswith('<') and 'HTMLBLOCK' not in p else p
        for p in paragraphs
    )
    return text


def load_css():
    """Load CSS file (cached after first read)."""
    global _cached_css
    if _cached_css is not None:
        return _cached_css
    css_path = Path(__file__).parent / "style.css"
    if not css_path.exists():
        raise FileNotFoundError("❌ style.css not found - cannot build site")
    _cached_css = css_path.read_text(encoding="utf-8")
    return _cached_css


def load_template():
    """Load HTML template (cached after first read)."""
    global _cached_template
    if _cached_template is not None:
        return _cached_template
    template_path = Path(__file__).parent / "template.html"
    if not template_path.exists():
        raise FileNotFoundError("❌ template.html not found - cannot build site")
    _cached_template = template_path.read_text(encoding="utf-8")
    return _cached_template


def render_html(title, content, description=None, canonical_path="/", schema_type="WebPage"):
    """Render complete HTML page from template."""
    template = load_template()
    css = load_css()
    
    # Build navigation
    nav_html = '\n                '.join(
        f'<a href="{url}">{name}</a>' for name, url in NAV_LINKS
    )
    
    # Build canonical URL
    canonical_url = f"{SITE_URL}{canonical_path}"
    
    # Build Schema.org JSON-LD
    schema_json = _build_schema_json(title, description or SITE_DESC, canonical_url, schema_type)
    
    # Fill template
    page_title = f"{title} - {SITE_TITLE}" if title != SITE_TITLE else title
    html_output = template.replace("{{title}}", page_title)
    html_output = html_output.replace("{{description}}", description or SITE_DESC)
    html_output = html_output.replace("{{canonical_url}}", canonical_url)
    html_output = html_output.replace("{{schema_json}}", schema_json)
    html_output = html_output.replace("{{site_title}}", SITE_TITLE)
    html_output = html_output.replace("{{site_desc}}", SITE_DESC)
    html_output = html_output.replace("{{navigation}}", nav_html)
    html_output = html_output.replace("{{content}}", content)
    html_output = html_output.replace("{{css}}", css)
    html_output = html_output.replace("{{year}}", str(datetime.now().year))
    
    return html_output


def _build_schema_json(title, description, url, schema_type):
    """Build Schema.org JSON-LD for SEO."""
    # Base Person schema (always present)
    person_schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Issa Sanogo",
        "url": SITE_URL,
        "jobTitle": "Senior Data Engineer",
        "description": "Senior Data Engineer — Data platforms & data quality",
        "sameAs": [
            "https://www.linkedin.com/in/ngsanogo/",
            "https://github.com/ngsanogo"
        ],
        "knowsAbout": [
            "Data Engineering",
            "Python",
            "SQL",
            "ETL",
            "Data Warehouse",
            "Apache Airflow",
            "Docker",
            "PostgreSQL"
        ]
    }
    
    # Page-specific schema
    page_schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": title,
        "description": description,
        "url": url,
        "author": {
            "@type": "Person",
            "name": "Issa Sanogo"
        }
    }
    
    # Combine schemas
    if schema_type == "WebPage" and url == SITE_URL + "/":
        # Homepage: include Website schema
        schemas = [
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "Issa Sanogo",
                "url": SITE_URL,
                "description": SITE_DESC
            },
            person_schema
        ]
    elif schema_type == "Article":
        schemas = [page_schema]
    else:
        schemas = [page_schema, person_schema]
    
    # Generate script tags
    script_tags = "\n    ".join(
        f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
        for s in schemas
    )
    return script_tags


def render_post_item(post):
    """Render a single post item HTML.
    
    Args:
        post: Post dictionary with slug, title, date_str, description
    
    Returns:
        str: HTML for post item
    """
    return f"""
    <div class="post-item">
        <h2 class="post-title"><a href="/posts/{post['slug']}">{post['title']}</a></h2>
        <div class="post-meta"><span>{post['date_str']}</span></div>
        <p class="post-description">{post['description']}</p>
        <a href="/posts/{post['slug']}" class="read-more">Read more →</a>
    </div>
    """


def render_pagination(current_page, total_pages, base_url="/blog"):
    """Render pagination HTML.
    
    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        base_url: Base URL for pagination links
    
    Returns:
        str: HTML for pagination
    """
    if total_pages <= 1:
        return ""
    
    html = '<div class="pagination">'
    
    # Previous button
    if current_page > 1:
        prev_url = base_url if current_page == 2 else f"{base_url}/page/{current_page - 1}"
        html += f'<a href="{prev_url}" class="read-more">← Previous</a>'
    else:
        html += '<span></span>'
    
    # Page numbers
    html += '<div class="page-numbers">'
    for i in range(1, total_pages + 1):
        page_url = base_url if i == 1 else f"{base_url}/page/{i}"
        if i == current_page:
            html += f'<span>{i}</span>'
        else:
            html += f'<a href="{page_url}">{i}</a>'
    html += '</div>'
    
    # Next button
    if current_page < total_pages:
        html += f'<a href="{base_url}/page/{current_page + 1}" class="read-more">Next →</a>'
    else:
        html += '<span></span>'
    
    html += '</div>'
    return html


def _validate_post_meta(meta, filename):
    """Validate post metadata.
    
    Args:
        meta: Metadata dictionary
        filename: Filename for error messages
    
    Returns:
        list: List of error messages (empty if valid)
    """
    errors = []
    
    if not meta.get("title"):
        errors.append(f"{filename}: Missing 'title'")
    
    if not meta.get("date"):
        errors.append(f"{filename}: Missing 'date'")
    elif not parse_date(meta.get("date")):
        errors.append(f"{filename}: Invalid date format")
    
    return errors


def _parse_post_file(file_path):
    """Parse a single post file.
    
    Args:
        file_path: Path to markdown file
    
    Returns:
        dict: Post data or None if invalid/draft
    """
    meta, body = parse_markdown_file(file_path)
    
    # Validate
    errors = _validate_post_meta(meta, file_path.name)
    if errors:
        for error in errors:
            logger.warning(f"{error} - skipping")
        return None
    
    # Skip drafts
    if meta.get("draft", "false").lower() == "true":
        return None
    
    # Parse dates
    date = parse_date(meta.get("date"))
    updated = parse_date(meta.get("updated")) or date
    
    return {
        "title": meta.get("title"),
        "slug": meta.get("slug", file_path.stem),
        "date": date,
        "updated": updated,
        "date_str": date.strftime(DATE_FORMAT),
        "updated_str": updated.strftime(DATE_FORMAT) if updated != date else None,
        "description": meta.get("description", ""),
        "body": markdown_to_html(body),
    }


def get_posts():
    """Return all published blog posts, sorted by date (newest first)."""
    posts_dir = CONTENT_DIR / "posts"
    if not posts_dir.exists():
        logger.warning(f"Posts directory '{posts_dir}' not found")
        return []
    posts = []
    for md_file in posts_dir.glob("*.md"):
        if md_file.name.startswith("_"):
            continue
        post = _parse_post_file(md_file)
        if post:
            posts.append(post)
    return sorted(posts, key=lambda x: x["date"], reverse=True)


def build_home(posts=None):
    """Build homepage. Uses posts if provided, else loads via get_posts()."""
    if posts is None:
        posts = get_posts()
    
    # Home page intro - clear value proposition in 5 seconds
    home_intro = """
        <div style="text-align: center;">
            <h1 class="page-title">Issa Sanogo</h1>
            <p class="tagline">Senior Data Engineer</p>
        </div>
        
        <div class="highlight-box">
            <p>I build <strong>data platforms</strong> and ensure <strong>data quality</strong> in contexts where reliability is non-negotiable.</p>
        </div>
        
        <p class="home-context" style="text-align: center;">8 years of experience in healthcare, medical research, and SaaS. I scope business needs, build solutions that last, and enable teams.</p>
        
        <p style="margin-top: 2rem; text-align: center;">
            <a href="/about" class="cta-button">Learn more</a>
            <a href="/contact" class="read-more" style="margin-left: 1.5rem;">Get in touch →</a>
        </p>
    """
    
    if not posts:
        content = home_intro
    else:
        latest_created = posts[0]
        
        posts_html = f"""
        <section class="home-section">
            <h2 class="section-title">Latest Writing</h2>
            {render_post_item(latest_created)}
            <p style="text-align: center;"><a href="/blog" class="read-more">View all posts →</a></p>
        </section>
        """
        
        content = f"""
        {home_intro}
        {posts_html}
        """
    
    html = render_html(
        SITE_TITLE, 
        content, 
        "Issa Sanogo - Senior Data Engineer. Data platforms, data quality, cross-functional project leadership.",
        canonical_path="/",
        schema_type="WebPage"
    )
    with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)


def _calculate_total_pages(total_posts, posts_per_page):
    """Calculate total number of pages for pagination.
    
    Args:
        total_posts: Total number of posts
        posts_per_page: Posts per page
    
    Returns:
        int: Total pages needed
    """
    return (total_posts + posts_per_page - 1) // posts_per_page


def _get_page_posts(posts, page_num, posts_per_page):
    """Get posts for a specific page.
    
    Args:
        posts: List of all posts
        page_num: Page number (1-indexed)
        posts_per_page: Posts per page
    
    Returns:
        list: Posts for the page
    """
    start_idx = (page_num - 1) * posts_per_page
    end_idx = start_idx + posts_per_page
    return posts[start_idx:end_idx]


def _build_blog_page_content(posts, page_num, total_pages):
    """Build content for a blog page.
    
    Args:
        posts: Posts to display on this page
        page_num: Current page number
        total_pages: Total number of pages
    
    Returns:
        str: HTML content for the page
    """
    posts_html = "".join(render_post_item(post) for post in posts)
    pagination_html = render_pagination(page_num, total_pages, "/blog")
    page_info = f" (Page {page_num} of {total_pages})" if total_pages > 1 else ""
    
    return f"""
        <h1 class="page-title" style="text-align: center;">Writing</h1>
        <p style="text-align: center;">Articles on data engineering, tools, and best practices.{page_info}</p>
        {posts_html}
        {pagination_html}
    """


def _write_blog_page(html_content, page_num, total_pages):
    """Write blog page to file.
    
    Args:
        html_content: HTML content to write
        page_num: Page number (1-indexed)
        total_pages: Total pages (for description)
    """
    description = (
        f"Data Engineering Blog - Articles on ETL, Python, SQL, data pipelines. "
        f"Page {page_num} of {total_pages}." if total_pages > 1 
        else "Data Engineering Blog - Articles on ETL, Python, SQL, data pipelines and best practices."
    )
    canonical_path = "/blog" if page_num == 1 else f"/blog/page/{page_num}"
    html = render_html("Writing", html_content, description, canonical_path=canonical_path)
    
    if page_num == 1:
        output_path = OUTPUT_DIR / "blog" / "index.html"
    else:
        page_dir = OUTPUT_DIR / "blog" / "page" / str(page_num)
        page_dir.mkdir(exist_ok=True, parents=True)
        output_path = page_dir / "index.html"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def build_blog(posts=None):
    """Build blog with pagination. Uses posts if provided, else loads via get_posts()."""
    if posts is None:
        posts = get_posts()
    total_pages = _calculate_total_pages(len(posts), POSTS_PER_PAGE)
    
    (OUTPUT_DIR / "blog").mkdir(exist_ok=True)
    
    for page_num in range(1, total_pages + 1):
        page_posts = _get_page_posts(posts, page_num, POSTS_PER_PAGE)
        content = _build_blog_page_content(page_posts, page_num, total_pages)
        _write_blog_page(content, page_num, total_pages)


def build_posts(posts=None):
    """Build individual blog post pages. Uses posts if provided, else loads via get_posts()."""
    if posts is None:
        posts = get_posts()
    (OUTPUT_DIR / "posts").mkdir(exist_ok=True)
    
    for post in posts:
        content = f"""
        <h1 class="page-title">{post['title']}</h1>
        <div class="post-meta"><span>{post['date_str']}</span></div>
        {post['body']}
        """
        
        description = post['description'] or f"{post['title']} - {SITE_DESC}"
        canonical_path = f"/posts/{post['slug']}"
        html = render_html(post['title'], content, description, canonical_path=canonical_path, schema_type="Article")
        post_dir = OUTPUT_DIR / "posts" / post['slug']
        post_dir.mkdir(exist_ok=True, parents=True)
        
        with open(post_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build_pages():
    """Build static pages (about, cv, contact, projects)."""
    default_descriptions = {
        "about": "Senior Data Engineer — data platforms, data quality, cross-functional leadership. Issa Sanogo.",
        "cv": "Resume — Issa Sanogo, Senior Data Engineer. Data platforms, ETL, data quality.",
        "contact": "Contact Issa Sanogo — Senior Data Engineer. Consulting and collaborations.",
        "projects": "Projects — data engineering and data platform work by Issa Sanogo.",
    }

    for page_name in STATIC_PAGES:
        page_file = CONTENT_DIR / f"{page_name}.md"
        
        if not page_file.exists():
            continue
        
        meta, body = parse_markdown_file(page_file)
        title = meta.get("title", page_name.capitalize())
        # Use description from frontmatter if available, else use default
        description = meta.get("description") or default_descriptions.get(page_name, SITE_DESC)
        
        # Remove the first H1 from body if it exists (we add our own with page-title class)
        body = re.sub(r'^#\s+.*?$', '', body, count=1, flags=re.MULTILINE).strip()
        
        content = f"""
        <h1 class="page-title">{title}</h1>
        {markdown_to_html(body)}
        """
        
        canonical_path = f"/{page_name}"
        html = render_html(title, content, description, canonical_path=canonical_path)
        page_dir = OUTPUT_DIR / page_name
        page_dir.mkdir(exist_ok=True)
        
        with open(page_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)


def build_sitemap(posts=None):
    """Build sitemap.xml for search engines. Uses posts if provided, else loads via get_posts()."""
    if posts is None:
        posts = get_posts()
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Homepage
    sitemap += f'  <url>\n    <loc>{SITE_URL}/</loc>\n'
    sitemap += f'    <priority>{SITEMAP_PRIORITIES["home"]}</priority>\n  </url>\n'
    
    # Blog
    sitemap += f'  <url>\n    <loc>{SITE_URL}/blog</loc>\n'
    sitemap += f'    <priority>{SITEMAP_PRIORITIES["blog"]}</priority>\n  </url>\n'
    
    for page in STATIC_PAGES:
        if (CONTENT_DIR / f"{page}.md").exists():
            sitemap += f'  <url>\n    <loc>{SITE_URL}/{page}</loc>\n'
            sitemap += f'    <priority>{SITEMAP_PRIORITIES["pages"]}</priority>\n  </url>\n'
    
    # Blog posts
    for post in posts:
        sitemap += f'  <url>\n    <loc>{SITE_URL}/posts/{post["slug"]}</loc>\n'
        sitemap += f'    <lastmod>{post["updated"].strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap += f'    <priority>{SITEMAP_PRIORITIES["posts"]}</priority>\n  </url>\n'
    
    sitemap += '</urlset>'
    
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def copy_static_files():
    """Copy static files (robots.txt, 404.html, favicon.svg) to output directory."""
    static_dir = Path(__file__).parent / "static"
    if not static_dir.exists():
        logger.warning(f"Static directory '{static_dir}' not found - skipping static files")
        return
    
    for static_file in static_dir.iterdir():
        if static_file.is_file():
            shutil.copy2(static_file, OUTPUT_DIR / static_file.name)


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
        logger.error("Missing required files:")
        for item in missing:
            logger.error(item)
        return False
    
    if not CONTENT_DIR.exists():
        logger.error(f"Content directory '{CONTENT_DIR}' not found")
        return False
    
    try:
        logger.info("🔨 Building site...")
        posts = get_posts()
        build_home(posts)
        logger.info("✓ Homepage built")
        build_blog(posts)
        logger.info("✓ Blog pages built")
        build_posts(posts)
        logger.info("✓ Individual posts built")
        build_pages()
        logger.info("✓ Static pages built")
        build_sitemap(posts)
        logger.info("✓ Sitemap generated")
        copy_static_files()
        logger.info("✓ Static files copied")
        logger.info(f"✅ Site built successfully in {OUTPUT_DIR}")
        return True
    except Exception as e:
        logger.error(f"Build failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    sys.exit(0 if build() else 1)
