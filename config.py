"""
config.py — Central configuration for the SEO/AEO Analyzer.

Supports two environments:
  - Local dev:       reads from .env file via python-dotenv
  - Streamlit Cloud: reads from st.secrets (set in the dashboard)
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Get a secret from .env (local) or st.secrets (Streamlit Cloud)."""
    # 1. Check environment variables / .env first
    value = os.environ.get(key, "")
    if value:
        return value

    # 2. Fall back to Streamlit secrets (Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return default


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")
BING_API_KEY = _get_secret("BING_API_KEY")

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
