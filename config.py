"""
config.py — Central configuration for the SEO/AEO Analyzer.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
BING_API_KEY = os.environ.get("BING_API_KEY", "")

# ---------------------------------------------------------------------------
# Google OAuth2
# ---------------------------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",          # GSC
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_DAYS = 90          # Performance data lookback window
DEFAULT_ROW_LIMIT = 1000   # Max rows from GSC / GA4
CRAWL_MAX_PAGES = 50       # Max pages to crawl in prospect mode
CRAWL_TIMEOUT = 10         # Seconds per HTTP request
GEMINI_MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Bing Webmaster API
# ---------------------------------------------------------------------------
BING_API_BASE = "https://ssl.bing.com/webmaster/api.svc/json"
