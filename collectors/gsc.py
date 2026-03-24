"""
gsc.py — Google Search Console Data Collector (Read-Only)

Fetches properties, performance data, and sitemap info from GSC.
"""

from datetime import datetime, timedelta
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from config import DEFAULT_DAYS, DEFAULT_ROW_LIMIT


def _get_service(creds: Credentials):
    """Build and return a Search Console API service object."""
    return build("webmasters", "v3", credentials=creds)


def list_properties(creds: Credentials) -> list[dict]:
    """
    Return every Search Console property the authenticated user can access.
    """
    service = _get_service(creds)
    response = service.sites().list().execute()
    sites = response.get("siteEntry", [])
    return [
        {
            "siteUrl": site.get("siteUrl", ""),
            "permissionLevel": site.get("permissionLevel", ""),
        }
        for site in sites
    ]


def fetch_performance(
    creds: Credentials,
    site_url: str,
    dimensions: list[str] = None,
    days: int = DEFAULT_DAYS,
    row_limit: int = DEFAULT_ROW_LIMIT,
) -> pd.DataFrame:
    """
    Fetch performance data from GSC with flexible dimensions.

    Args:
        dimensions: e.g. ["query"], ["page"], ["query", "page"]
    """
    if dimensions is None:
        dimensions = ["query"]

    service = _get_service(creds)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "dataState": "final",
        },
    ).execute()

    rows = response.get("rows", [])
    if not rows:
        cols = dimensions + ["clicks", "impressions", "ctr", "position"]
        return pd.DataFrame(columns=cols)

    data = []
    for row in rows:
        entry = {}
        for i, dim in enumerate(dimensions):
            entry[dim] = row["keys"][i]
        entry["clicks"] = row.get("clicks", 0)
        entry["impressions"] = row.get("impressions", 0)
        entry["ctr"] = round(row.get("ctr", 0) * 100, 2)
        entry["position"] = round(row.get("position", 0), 1)
        data.append(entry)

    df = pd.DataFrame(data)
    df = df.sort_values("clicks", ascending=False).reset_index(drop=True)
    return df


def fetch_sitemaps(creds: Credentials, site_url: str) -> list[dict]:
    """Fetch submitted sitemaps and their status."""
    service = _get_service(creds)
    try:
        response = service.sitemaps().list(siteUrl=site_url).execute()
        sitemaps = response.get("sitemap", [])
        return [
            {
                "path": sm.get("path", ""),
                "type": sm.get("type", ""),
                "lastSubmitted": sm.get("lastSubmitted", ""),
                "isPending": sm.get("isPending", False),
                "isSitemapsIndex": sm.get("isSitemapsIndex", False),
                "warnings": sm.get("warnings", 0),
                "errors": sm.get("errors", 0),
            }
            for sm in sitemaps
        ]
    except Exception:
        return []


def collect_all(creds: Credentials, site_url: str) -> dict:
    """
    Collect all GSC data for a property. Returns a structured dict.
    """
    df_queries = fetch_performance(creds, site_url, ["query"])
    df_pages = fetch_performance(creds, site_url, ["page"])
    df_query_pages = fetch_performance(creds, site_url, ["query", "page"])
    sitemaps = fetch_sitemaps(creds, site_url)

    # Striking distance keywords (position 11-20)
    striking = df_queries[
        (df_queries["position"] >= 11) & (df_queries["position"] <= 20)
    ].copy() if not df_queries.empty else pd.DataFrame()

    # Top opportunity keywords (high impressions, low CTR)
    opportunities = pd.DataFrame()
    if not df_queries.empty:
        opportunities = df_queries[
            (df_queries["impressions"] >= 100) & (df_queries["ctr"] < 3.0)
        ].sort_values("impressions", ascending=False).head(20)

    return {
        "queries": df_queries,
        "pages": df_pages,
        "query_pages": df_query_pages,
        "sitemaps": sitemaps,
        "striking_distance": striking,
        "low_ctr_opportunities": opportunities,
        "summary": {
            "total_clicks": int(df_queries["clicks"].sum()) if not df_queries.empty else 0,
            "total_impressions": int(df_queries["impressions"].sum()) if not df_queries.empty else 0,
            "avg_ctr": round(df_queries["ctr"].mean(), 2) if not df_queries.empty else 0,
            "avg_position": round(df_queries["position"].mean(), 1) if not df_queries.empty else 0,
            "total_queries": len(df_queries),
            "total_pages": len(df_pages),
            "sitemap_count": len(sitemaps),
        },
    }
