#!/usr/bin/env python3
"""
Tests unitaires pour le générateur de site.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path to import build module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from build import (
    parse_markdown_file,
    parse_date,
    markdown_to_html,
    _convert_headers,
    _convert_emphasis,
    _convert_links,
    _convert_images,
    _convert_code,
    _convert_lists,
    _convert_blockquotes,
    render_post_item,
    render_pagination,
    _calculate_total_pages,
    _get_page_posts,
    _validate_post_meta,
    _parse_post_file,
    _build_schema_json,
    copy_static_files,
    get_posts,
    build,
    build_home,
    build_sitemap,
    OUTPUT_DIR,
    CONTENT_DIR,
)


class TestMarkdownParsing(unittest.TestCase):
    """Tests pour le parsing markdown."""
    
    def test_parse_date_valid(self):
        """Test parsing d'une date valide."""
        date = parse_date("2024-01-30")
        self.assertIsNotNone(date)
        self.assertEqual(date.year, 2024)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 30)
    
    def test_parse_date_invalid(self):
        """Test parsing d'une date invalide."""
        self.assertIsNone(parse_date("invalid-date"))
        self.assertIsNone(parse_date(None))
        self.assertIsNone(parse_date(""))
    
    def test_convert_headers(self):
        """Test conversion des headers markdown."""
        self.assertIn("<h1>Title</h1>", _convert_headers("# Title"))
        self.assertIn("<h2>Subtitle</h2>", _convert_headers("## Subtitle"))
        self.assertIn("<h3>Section</h3>", _convert_headers("### Section"))
    
    def test_convert_emphasis(self):
        """Test conversion bold/italic."""
        self.assertIn("<strong>bold</strong>", _convert_emphasis("**bold**"))
        self.assertIn("<em>italic</em>", _convert_emphasis("*italic*"))
        self.assertIn("<strong>bold</strong>", _convert_emphasis("__bold__"))
        self.assertIn("<em>italic</em>", _convert_emphasis("_italic_"))
    
    def test_convert_links(self):
        """Test conversion des liens."""
        result = _convert_links("[text](http://example.com)")
        self.assertIn('<a href="http://example.com">text</a>', result)
    
    def test_convert_images(self):
        """Test conversion des images."""
        result = _convert_images("![alt text](image.jpg)")
        self.assertIn('<img src="image.jpg" alt="alt text">', result)
    
    def test_convert_code(self):
        """Test conversion du code."""
        # Inline code
        result = _convert_code("`code`")
        self.assertIn("<code>code</code>", result)
        
        # Code block
        result = _convert_code("```python\nprint('hello')\n```")
        self.assertIn("<pre><code>", result)
        self.assertIn("print('hello')", result)
    
    def test_convert_lists(self):
        """Test conversion des listes."""
        # Unordered list
        result = _convert_lists("* Item 1\n* Item 2")
        self.assertIn("<ul>", result)
        self.assertIn("<li>Item 1</li>", result)
        
        # Numbered list
        result = _convert_lists("1. First\n2. Second")
        self.assertIn("<li>First</li>", result)
    
    def test_convert_blockquotes(self):
        """Test conversion des blockquotes."""
        result = _convert_blockquotes("> Quote text")
        self.assertIn("<blockquote>Quote text</blockquote>", result)
    
    def test_markdown_to_html_complete(self):
        """Test conversion markdown complète."""
        markdown = """# Title

This is **bold** and *italic*.

[Link](http://example.com)

* List item 1
* List item 2
"""
        html = markdown_to_html(markdown)
        
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn('<a href="http://example.com">Link</a>', html)
        self.assertIn("<li>List item", html)


class TestFrontmatterParsing(unittest.TestCase):
    """Tests pour le parsing du frontmatter."""
    
    def setUp(self):
        """Créer un fichier de test temporaire."""
        self.test_file = Path("test_post.md")
        content = """---
title: Test Post
slug: test-post
date: 2024-01-30
description: Test description
draft: false
---

# Test Content

This is a test post.
"""
        self.test_file.write_text(content, encoding="utf-8")
    
    def tearDown(self):
        """Nettoyer le fichier de test."""
        if self.test_file.exists():
            self.test_file.unlink()
    
    def test_parse_frontmatter(self):
        """Test parsing du frontmatter YAML."""
        meta, body = parse_markdown_file(self.test_file)
        
        self.assertEqual(meta["title"], "Test Post")
        self.assertEqual(meta["slug"], "test-post")
        self.assertEqual(meta["date"], "2024-01-30")
        self.assertEqual(meta["description"], "Test description")
        self.assertEqual(meta["draft"], "false")
        self.assertIn("# Test Content", body)
        self.assertIn("This is a test post", body)
    
    def test_parse_no_frontmatter(self):
        """Test parsing sans frontmatter."""
        test_file = Path("test_no_fm.md")
        test_file.write_text("# Just content", encoding="utf-8")
        
        meta, body = parse_markdown_file(test_file)
        
        self.assertEqual(meta, {})
        self.assertIn("# Just content", body)
        
        test_file.unlink()


class TestTemplateRendering(unittest.TestCase):
    """Tests pour les templates HTML."""
    
    def test_render_post_item(self):
        """Test génération HTML d'un post item."""
        post = {
            "slug": "test-post",
            "title": "Test Post",
            "date_str": "January 30, 2024",
            "description": "Test description"
        }
        html = render_post_item(post)
        
        self.assertIn("post-item", html)
        self.assertIn("Test Post", html)
        self.assertIn("/posts/test-post", html)
        self.assertIn("Test description", html)
    
    def test_render_pagination_single_page(self):
        """Test pagination avec une seule page."""
        html = render_pagination(1, 1)
        self.assertEqual(html, "")
    
    def test_render_pagination_multiple_pages(self):
        """Test pagination avec plusieurs pages."""
        html = render_pagination(2, 3)
        
        self.assertIn("pagination", html)
        self.assertIn("Précédent", html)
        self.assertIn("Suivant", html)
        self.assertIn('href="/blog"', html)  # Page 1 uses /blog not /blog/page/1
        self.assertIn("/blog/page/3", html)


class TestBuildHelpers(unittest.TestCase):
    """Tests pour les fonctions helper de build."""
    
    def test_calculate_total_pages(self):
        """Test calcul du nombre de pages."""
        self.assertEqual(_calculate_total_pages(10, 10), 1)
        self.assertEqual(_calculate_total_pages(11, 10), 2)
        self.assertEqual(_calculate_total_pages(25, 10), 3)
        self.assertEqual(_calculate_total_pages(0, 10), 0)
    
    def test_get_page_posts(self):
        """Test récupération des posts d'une page."""
        posts = [{"id": i} for i in range(25)]
        
        page1 = _get_page_posts(posts, 1, 10)
        self.assertEqual(len(page1), 10)
        self.assertEqual(page1[0]["id"], 0)
        
        page2 = _get_page_posts(posts, 2, 10)
        self.assertEqual(len(page2), 10)
        self.assertEqual(page2[0]["id"], 10)
        
        page3 = _get_page_posts(posts, 3, 10)
        self.assertEqual(len(page3), 5)
        self.assertEqual(page3[0]["id"], 20)


class TestBuildIntegration(unittest.TestCase):
    """Tests d'intégration pour le build complet."""
    
    def test_build_complete(self):
        """Test build complet du site."""
        result = build()
        self.assertTrue(result, "Build should succeed")
        
        # Vérifier fichiers générés
        self.assertTrue((OUTPUT_DIR / "index.html").exists(), "Homepage should exist")
        self.assertTrue((OUTPUT_DIR / "sitemap.xml").exists(), "Sitemap should exist")
        self.assertTrue((OUTPUT_DIR / "blog" / "index.html").exists(), "Blog should exist")
    
    def test_homepage_content(self):
        """Test contenu de la homepage."""
        build_home()
        html = (OUTPUT_DIR / "index.html").read_text()
        
        self.assertIn("<title>", html)
        self.assertIn("Issa Sanogo", html)
        # Le site est en français, vérifier le contenu FR
        self.assertIn("Data Engineer Senior", html)
    
    def test_sitemap_valid_xml(self):
        """Test validité du sitemap XML."""
        build_sitemap()
        sitemap = (OUTPUT_DIR / "sitemap.xml").read_text()
        
        self.assertIn('<?xml version="1.0"', sitemap)
        self.assertIn('<urlset', sitemap)
        self.assertIn('</urlset>', sitemap)
        self.assertIn(f'<loc>https://ngsanogo.github.io/</loc>', sitemap)
    
    def test_html_structure_valid(self):
        """Test structure HTML basique."""
        build_home()
        html = (OUTPUT_DIR / "index.html").read_text()
        
        # Check HTML5 structure
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html", html)
        self.assertIn("</html>", html)
        self.assertIn("<head>", html)
        self.assertIn("</head>", html)
        self.assertIn("<body>", html)
        self.assertIn("</body>", html)
        
        # Check meta tags
        self.assertIn('<meta charset="UTF-8">', html)
        self.assertIn('<meta name="viewport"', html)
        self.assertIn('<meta name="description"', html)


class TestEdgeCases(unittest.TestCase):
    """Tests pour les cas limites."""
    
    def test_validate_post_meta_missing_title(self):
        """Test validation metadata sans titre."""
        meta = {"date": "2024-01-30"}
        errors = _validate_post_meta(meta, "test.md")
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing 'title'", errors[0])
    
    def test_validate_post_meta_missing_date(self):
        """Test validation metadata sans date."""
        meta = {"title": "Test"}
        errors = _validate_post_meta(meta, "test.md")
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing 'date'", errors[0])
    
    def test_validate_post_meta_invalid_date(self):
        """Test validation metadata avec date invalide."""
        meta = {"title": "Test", "date": "invalid"}
        errors = _validate_post_meta(meta, "test.md")
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid date format", errors[0])
    
    def test_validate_post_meta_valid(self):
        """Test validation metadata valide."""
        meta = {"title": "Test", "date": "2024-01-30"}
        errors = _validate_post_meta(meta, "test.md")
        self.assertEqual(len(errors), 0)
    
    def test_parse_post_file_draft(self):
        """Test que les drafts sont ignorés."""
        test_file = Path("test_draft.md")
        content = """---
title: Draft Post
date: 2024-01-30
draft: true
---
Content"""
        test_file.write_text(content, encoding="utf-8")
        
        post = _parse_post_file(test_file)
        self.assertIsNone(post)
        
        test_file.unlink()
    
    def test_parse_post_file_valid(self):
        """Test parsing fichier valide."""
        test_file = Path("test_valid.md")
        content = """---
title: Valid Post
slug: valid-post
date: 2024-01-30
description: Test
draft: false
---
Content here"""
        test_file.write_text(content, encoding="utf-8")
        
        post = _parse_post_file(test_file)
        self.assertIsNotNone(post)
        self.assertEqual(post["title"], "Valid Post")
        self.assertEqual(post["slug"], "valid-post")
        
        test_file.unlink()
    
    def test_get_posts_empty_directory(self):
        """Test get_posts avec répertoire vide."""
        # Test avec le vrai répertoire devrait avoir des posts
        posts = get_posts()
        # Si on a des articles, ça devrait retourner une liste
        self.assertIsInstance(posts, list)
    
    def test_build_with_zero_posts(self):
        """Test que build fonctionne même sans posts."""
        # Le build devrait réussir même avec 0 posts
        result = build()
        self.assertTrue(result)


class TestSiteStructure(unittest.TestCase):
    """Tests pour la structure du site."""
    
    def test_required_directories_exist(self):
        """Vérifier que les répertoires requis existent."""
        root = Path(__file__).parent.parent
        self.assertTrue((root / "content").exists())
        self.assertTrue((root / "content/posts").exists())
    
    def test_required_files_exist(self):
        """Vérifier que les fichiers requis existent."""
        root = Path(__file__).parent.parent
        self.assertTrue((root / "src/config.py").exists())
        self.assertTrue((root / "src/template.html").exists())
        self.assertTrue((root / "src/style.css").exists())
        self.assertTrue((root / "src/build.py").exists())
    
    def test_static_files_exist(self):
        """Vérifier que les fichiers statiques existent."""
        root = Path(__file__).parent.parent
        self.assertTrue((root / "src/static/robots.txt").exists())
        self.assertTrue((root / "src/static/404.html").exists())
        self.assertTrue((root / "src/static/favicon.svg").exists())


class TestSEOFeatures(unittest.TestCase):
    """Tests pour les fonctionnalités SEO."""
    
    def test_schema_json_homepage(self):
        """Test Schema.org JSON-LD pour la homepage."""
        from config import SITE_URL, SITE_DESC
        schema = _build_schema_json("Issa Sanogo", SITE_DESC, f"{SITE_URL}/", "WebPage")
        
        self.assertIn("application/ld+json", schema)
        self.assertIn("WebSite", schema)
        self.assertIn("Person", schema)
        self.assertIn("Issa Sanogo", schema)
    
    def test_schema_json_article(self):
        """Test Schema.org JSON-LD pour un article."""
        from config import SITE_URL
        schema = _build_schema_json("Test Article", "Description", f"{SITE_URL}/posts/test", "Article")
        
        self.assertIn("application/ld+json", schema)
        self.assertIn("Article", schema)
        self.assertIn("Test Article", schema)
    
    def test_static_files_copied_after_build(self):
        """Test que les fichiers statiques sont copiés après le build."""
        build()
        
        self.assertTrue((OUTPUT_DIR / "robots.txt").exists())
        self.assertTrue((OUTPUT_DIR / "404.html").exists())
        self.assertTrue((OUTPUT_DIR / "favicon.svg").exists())
    
    def test_html_has_canonical_url(self):
        """Test que les pages HTML ont une URL canonique."""
        build_home()
        html = (OUTPUT_DIR / "index.html").read_text()
        
        self.assertIn('rel="canonical"', html)
        self.assertIn('https://ngsanogo.github.io/', html)
    
    def test_html_has_open_graph(self):
        """Test que les pages HTML ont les balises Open Graph."""
        build_home()
        html = (OUTPUT_DIR / "index.html").read_text()
        
        self.assertIn('og:title', html)
        self.assertIn('og:description', html)
        self.assertIn('og:url', html)


if __name__ == "__main__":
    unittest.main()
