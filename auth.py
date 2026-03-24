"""
auth.py — Google OAuth2 Authentication (Read-Only)

Authenticates using credentials.json and caches the token in token.json.
Supports scopes for GSC, GA4, and Google Business Profile.
"""

# ============================================================
# SAFETY: THIS TOOL IS 100% READ-ONLY
#
# OAuth Scopes requested:
#   - webmasters.readonly      → GSC read-only
#   - analytics.readonly       → GA4 read-only
#   - business.manage          → GBP (scope name is "manage" but
#                                 we ONLY call list/get methods)
#
# API Methods used (every single one is read-only):
#   GSC:  sites().list(), searchanalytics().query(), sitemaps().list()
#   GA4:  accounts().list(), properties().list(), run_report()
#   GBP:  accounts().list(), locations().list(), reviews().list()
#   Bing: GET requests only (GetQueryStats, GetPageStats, etc.)
#
# NO update/delete/post/create/patch methods are called ANYWHERE.
# ============================================================

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import SCOPES, TOKEN_PATH, CREDENTIALS_PATH

import os


def get_credentials() -> Credentials:
    """
    Return valid Google OAuth2 credentials.

    - If a cached token.json exists and is still valid, reuse it.
    - If the token is expired but has a refresh token, refresh it.
    - Otherwise, launch the OAuth consent flow in the browser.
    """
    creds = None

    # 1. Try to load cached token
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # 2. Refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_PATH}. "
                    "Download it from the Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # 3. Cache the token
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds


if __name__ == "__main__":
    credentials = get_credentials()
    print("✅ Authentication successful!")
    print(f"   Token cached at: {TOKEN_PATH}")
    print(f"   Scopes: {SCOPES}")
