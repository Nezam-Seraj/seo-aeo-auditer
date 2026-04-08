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


def fetch_site_totals(
    creds: Credentials,
    site_url: str,
    days: int = DEFAULT_DAYS,
) -> dict:
    """
    Fetch TRUE site-wide totals from GSC using a dimensionless query.

    A dimensionless query has no row limit — it returns the aggregate
    clicks, impressions, CTR, and position for the ENTIRE site.
    This prevents underestimation when the per-query breakdown is
    capped by row limits.
    """
    service = _get_service(creds)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dataState": "final",
            # No "dimensions" key = aggregate totals, no row limit
        },
    ).execute()

    rows = response.get("rows", [])
    if rows:
        row = rows[0]
        return {
            "total_clicks": int(row.get("clicks", 0)),
            "total_impressions": int(row.get("impressions", 0)),
            "avg_ctr": round(row.get("ctr", 0) * 100, 2),
            "avg_position": round(row.get("position", 0), 1),
        }

    return {
        "total_clicks": 0,
        "total_impressions": 0,
        "avg_ctr": 0,
        "avg_position": 0,
    }


def collect_all(creds: Credentials, site_url: str) -> dict:
    """
    Collect all GSC data for a property. Returns a structured dict.

    Uses a dimensionless query for TRUE site-wide totals (no row limit),
    plus per-query and per-page breakdowns for detailed analysis.
    """
    # TRUE site-wide totals (dimensionless = no row limit)
    site_totals = fetch_site_totals(creds, site_url)

    # Detailed breakdowns (subject to row_limit, used for drill-down)
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
        ].sort_values("impressions", ascending=False).head(50)

    # Calculate what % of total impressions our query rows cover
    queried_impressions = int(df_queries["impressions"].sum()) if not df_queries.empty else 0
    true_impressions = site_totals["total_impressions"]
    coverage_pct = round((queried_impressions / true_impressions * 100), 1) if true_impressions > 0 else 0

    return {
        "queries": df_queries,
        "pages": df_pages,
        "query_pages": df_query_pages,
        "sitemaps": sitemaps,
        "striking_distance": striking,
        "low_ctr_opportunities": opportunities,
        "summary": {
            # TRUE site-wide totals (from dimensionless query — always accurate)
            "total_clicks": site_totals["total_clicks"],
            "total_impressions": site_totals["total_impressions"],
            "avg_ctr": site_totals["avg_ctr"],
            "avg_position": site_totals["avg_position"],
            # Breakdown coverage
            "queried_impressions": queried_impressions,
            "query_coverage_pct": coverage_pct,
            "total_queries": len(df_queries),
            "total_pages": len(df_pages),
            "sitemap_count": len(sitemaps),
        },
    }
