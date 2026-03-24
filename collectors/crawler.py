"""
crawler.py — Public Site Crawler for Prospect/Competitor Mode

Crawls publicly available data from any website:
- Page content, headings, meta tags
- Technical SEO signals (robots.txt, sitemap, HTTPS, etc.)
- Schema markup / structured data
- Internal link structure
"""

import re
import json
import time
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

from config import CRAWL_MAX_PAGES, CRAWL_TIMEOUT

# Common non-English language path segments to skip
_NON_ENGLISH_PATHS = {
    "/es/", "/fr/", "/de/", "/it/", "/pt/", "/ja/", "/ko/", "/zh/",
    "/ru/", "/ar/", "/nl/", "/pl/", "/sv/", "/da/", "/fi/", "/no/",
    "/tr/", "/vi/", "/th/", "/id/", "/ms/", "/hi/", "/bn/", "/uk/",
    "/cs/", "/ro/", "/hu/", "/el/", "/he/", "/bg/", "/hr/", "/sk/",
    "/sl/", "/lt/", "/lv/", "/et/", "/ca/", "/gl/", "/eu/",
    "/es-", "/fr-", "/de-", "/pt-", "/zh-", "/ja-",
}


def _is_english_url(url: str) -> bool:
    """Check if a URL likely points to an English page based on path."""
    path = urlparse(url).path.lower()
    for lang_seg in _NON_ENGLISH_PATHS:
        if lang_seg in path:
            return False
    return True


def _is_english_page(soup: BeautifulSoup) -> bool:
    """Check if a page is English via the html lang attribute."""
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        lang = html_tag["lang"].lower().strip()
        # Accept en, en-US, en-GB, etc.
        return lang.startswith("en") or lang == ""
    # No lang attribute — assume English
    return True


@dataclass
class PageData:
    """Structured data from a single crawled page."""
    url: str = ""
    status_code: int = 0
    title: str = ""
    meta_description: str = ""
    h1: list[str] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)
    h3: list[str] = field(default_factory=list)
    word_count: int = 0
    internal_links: int = 0
    external_links: int = 0
    images_without_alt: int = 0
    total_images: int = 0
    has_canonical: bool = False
    canonical_url: str = ""
    schema_types: list[str] = field(default_factory=list)
    content_preview: str = ""
    load_time: float = 0.0


@dataclass
class TechnicalSEO:
    """Technical SEO signals from a site."""
    has_robots_txt: bool = False
    robots_txt_content: str = ""
    has_sitemap: bool = False
    sitemap_url: str = ""
    sitemap_page_count: int = 0
    uses_https: bool = False
    has_viewport_meta: bool = False
    pages_crawled: int = 0
    total_errors: int = 0
    avg_load_time: float = 0.0


def _get_session() -> requests.Session:
    """Create a requests session with browser-like headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    return session


def _extract_schema_types(data, schema_list: list):
    """Recursively extract @type values from JSON-LD, handling @graph and nested structures."""
    if isinstance(data, dict):
        # Handle @graph (array of entities inside a single JSON-LD block)
        if "@graph" in data:
            for item in data["@graph"]:
                _extract_schema_types(item, schema_list)
        # Handle @type (can be string or list)
        if "@type" in data:
            type_val = data["@type"]
            if isinstance(type_val, list):
                # e.g. ["Dentist", "MedicalClinic"] — take first as primary
                schema_list.extend(type_val)
            elif isinstance(type_val, str):
                schema_list.append(type_val)
    elif isinstance(data, list):
        for item in data:
            _extract_schema_types(item, schema_list)


def crawl_page(session: requests.Session, url: str, base_domain: str) -> PageData | None:
    """Crawl a single page and extract SEO-relevant data."""
    page = PageData(url=url)

    try:
        start = time.time()
        response = session.get(url, timeout=CRAWL_TIMEOUT, allow_redirects=True)
        page.load_time = round(time.time() - start, 2)
        page.status_code = response.status_code

        if response.status_code != 200:
            return page

        soup = BeautifulSoup(response.text, "lxml")

        # Skip non-English pages
        if not _is_english_page(soup):
            return None

        # Title
        title_tag = soup.find("title")
        page.title = title_tag.get_text(strip=True) if title_tag else ""

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        page.meta_description = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""

        # Headings
        page.h1 = [tag.get_text(strip=True) for tag in soup.find_all("h1")]
        page.h2 = [tag.get_text(strip=True) for tag in soup.find_all("h2")]
        page.h3 = [tag.get_text(strip=True) for tag in soup.find_all("h3")]

        # JS-rendered H1 fallback — if no H1 was found in static HTML,
        # check for H1 content inside inline JS / template strings and
        # detect JS CMS platforms that render headings client-side.
        if not page.h1:
            raw_html = response.text

            # 1. Look for <h1> tags inside inline JavaScript strings
            #    Matches patterns like: '<h1>Some Text</h1>' or "<h1 class=...>Text</h1>"
            js_h1_matches = re.findall(
                r'<h1[^>]*>(.*?)</h1>',
                raw_html,
                re.IGNORECASE | re.DOTALL,
            )
            # Filter out any that were already found by BS4 (i.e. visible in DOM)
            # and clean HTML entities
            for match in js_h1_matches:
                cleaned = re.sub(r'<[^>]+>', '', match).strip()
                cleaned = cleaned.replace('\\n', ' ').replace('\\t', ' ').strip()
                if cleaned and cleaned not in page.h1:
                    page.h1.append(cleaned)

            # 2. Detect JS CMS platforms that commonly render H1 via JavaScript
            if not page.h1:
                js_cms_indicators = {
                    'duda': ['dmPagesContext', 'duda', 'dudasite', 'dm-page'],
                    'wix': ['wix-site', 'wixCode', 'X-Wix', 'wix.com'],
                    'squarespace': ['squarespace', 'sqs-block'],
                    'webflow': ['webflow', 'w-nav', 'wf-page'],
                }
                detected_cms = None
                html_lower = raw_html.lower()
                for cms_name, markers in js_cms_indicators.items():
                    if any(marker.lower() in html_lower for marker in markers):
                        detected_cms = cms_name
                        break

                if detected_cms:
                    page.h1 = [f"[JS-rendered by {detected_cms.title()} — likely present, not extractable via static crawl]"]

        # Word count (body text only)
        body = soup.find("body")
        if body:
            text = body.get_text(separator=" ", strip=True)
            page.word_count = len(text.split())
            page.content_preview = text[:500]

        # Links — count and discover crawlable internal links
        page._discovered_links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(url, href).split("#")[0].rstrip("/")
            parsed = urlparse(full_url)
            if parsed.netloc == base_domain:
                page.internal_links += 1
                # Track for BFS discovery
                if (
                    parsed.scheme in ("http", "https")
                    and _is_english_url(full_url)
                    and not any(full_url.lower().endswith(ext) for ext in
                               (".pdf", ".jpg", ".png", ".gif", ".svg", ".css", ".js", ".xml"))
                ):
                    page._discovered_links.append(full_url)
            elif parsed.scheme in ("http", "https"):
                page.external_links += 1

        # Images
        for img in soup.find_all("img"):
            page.total_images += 1
            if not img.get("alt"):
                page.images_without_alt += 1

        # Canonical
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical and canonical.get("href"):
            page.has_canonical = True
            page.canonical_url = canonical["href"]

        # Schema/structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                _extract_schema_types(data, page.schema_types)
            except (json.JSONDecodeError, TypeError):
                pass

        return page

    except requests.RequestException:
        page.status_code = 0
        return page


def check_technical_seo(session: requests.Session, base_url: str) -> TechnicalSEO:
    """Check technical SEO signals for a site."""
    tech = TechnicalSEO()
    parsed = urlparse(base_url)
    tech.uses_https = parsed.scheme == "https"

    # robots.txt
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        r = session.get(robots_url, timeout=CRAWL_TIMEOUT)
        if r.status_code == 200:
            tech.has_robots_txt = True
            tech.robots_txt_content = r.text[:2000]

            # Look for sitemap in robots.txt
            for line in r.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    tech.sitemap_url = line.split(":", 1)[1].strip()
                    break
    except requests.RequestException:
        pass

    # sitemap.xml (check default location if not found in robots.txt)
    if not tech.sitemap_url:
        tech.sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

    try:
        r = session.get(tech.sitemap_url, timeout=CRAWL_TIMEOUT)
        if r.status_code == 200 and "<url>" in r.text.lower():
            tech.has_sitemap = True
            tech.sitemap_page_count = r.text.lower().count("<url>")
    except requests.RequestException:
        pass

    # Viewport meta
    try:
        r = session.get(base_url, timeout=CRAWL_TIMEOUT)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            viewport = soup.find("meta", attrs={"name": "viewport"})
            tech.has_viewport_meta = viewport is not None
    except requests.RequestException:
        pass

    return tech


def crawl_site(
    url: str,
    max_pages: int = CRAWL_MAX_PAGES,
    progress_callback=None,
) -> dict:
    """
    Crawl a website and collect SEO data.

    Args:
        url: The starting URL to crawl.
        max_pages: Maximum number of pages to crawl.
        progress_callback: Optional callable(current, total, url) for progress updates.

    Returns:
        Dict with 'pages', 'technical_seo', and 'summary'.
    """
    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    url = url.rstrip("/")

    parsed = urlparse(url)
    base_domain = parsed.netloc
    session = _get_session()

    # Check technical SEO first
    tech = check_technical_seo(session, url)

    # Crawl pages via BFS
    visited = set()
    queue = [url]
    pages = []

    while queue and len(pages) < max_pages:
        current_url = queue.pop(0)

        # Normalize
        current_url = current_url.split("#")[0].rstrip("/")
        if current_url in visited:
            continue
        visited.add(current_url)

        if progress_callback:
            progress_callback(len(pages) + 1, max_pages, current_url)

        page = crawl_page(session, current_url, base_domain)
        if page is None:
            continue

        pages.append(page)

        # Don't follow links from error pages
        if page.status_code != 200:
            tech.total_errors += 1
            continue

        # Use links already discovered during crawl_page
        for link_url in getattr(page, '_discovered_links', []):
            if link_url not in visited:
                queue.append(link_url)

        # Small delay to be respectful
        time.sleep(0.3)

    tech.pages_crawled = len(pages)
    load_times = [p.load_time for p in pages if p.load_time > 0]
    tech.avg_load_time = round(sum(load_times) / len(load_times), 2) if load_times else 0

    # Build summary
    total_words = sum(p.word_count for p in pages)
    pages_with_meta = sum(1 for p in pages if p.meta_description)
    pages_with_h1 = sum(1 for p in pages if p.h1)
    pages_with_schema = sum(1 for p in pages if p.schema_types)
    total_images = sum(p.total_images for p in pages)
    images_no_alt = sum(p.images_without_alt for p in pages)

    # Collect all schema types found
    all_schema_types = set()
    for p in pages:
        all_schema_types.update(p.schema_types)

    return {
        "pages": pages,
        "technical_seo": tech,
        "summary": {
            "pages_crawled": len(pages),
            "total_word_count": total_words,
            "avg_word_count": round(total_words / len(pages)) if pages else 0,
            "pages_with_meta_description": pages_with_meta,
            "pages_with_h1": pages_with_h1,
            "pages_with_schema": pages_with_schema,
            "schema_types_found": list(all_schema_types),
            "total_images": total_images,
            "images_without_alt": images_no_alt,
            "uses_https": tech.uses_https,
            "has_sitemap": tech.has_sitemap,
            "has_robots_txt": tech.has_robots_txt,
            "has_viewport_meta": tech.has_viewport_meta,
            "avg_load_time": tech.avg_load_time,
            "crawl_errors": tech.total_errors,
        },
    }
