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


if __name__ == "__main__":
    unittest.main()
