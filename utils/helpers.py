"""
helpers.py — Shared utility functions.
"""

from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """Normalize a URL by ensuring it has a scheme and stripping trailing slashes."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url.rstrip("/")


def extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    parsed = urlparse(normalize_url(url))
    return parsed.netloc


def truncate(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length, appending '...' if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_number(n: int | float) -> str:
    """Format a number with commas."""
    if isinstance(n, float):
        return f"{n:,.1f}"
    return f"{n:,}"
