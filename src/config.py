"""Site configuration - edit this file to change site settings."""

# Site information
SITE_TITLE = "Issa Sanogo"
SITE_DESC = "Senior Data Engineer — Data platforms & data quality"
SITE_URL = "https://ngsanogo.github.io"

# Build settings
POSTS_PER_PAGE = 10

# Navigation links (in order)
NAV_LINKS = [
    ("Home", "/"),
    ("About", "/about"),
    ("Work", "/projects"),
    ("Writing", "/blog"),
    ("Resume", "/cv"),
    ("Contact", "/contact"),
]

# Development server
DEV_SERVER_HOST = "localhost"
DEV_SERVER_PORT = 8000

# Date formatting
DATE_FORMAT = "%B %d, %Y"  # "January 30, 2024"

# Sitemap priorities
SITEMAP_PRIORITIES = {
    "home": 1.0,
    "blog": 0.9,
    "pages": 0.8,
    "posts": 0.6,
}
