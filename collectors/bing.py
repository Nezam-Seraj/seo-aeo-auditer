"""
bing.py — Bing Webmaster Tools Data Collector

Fetches traffic, keyword, crawl, and backlink data from Bing Webmaster API.
Uses API key authentication (not OAuth).
"""

import requests
import pandas as pd

from config import BING_API_BASE, BING_API_KEY


def _make_request(endpoint: str, params: dict = None, api_key: str = None) -> dict | list | None:
    """Make a GET request to the Bing Webmaster API."""
    key = api_key or BING_API_KEY
    if not key:
        return None

    if params is None:
        params = {}
    params["apikey"] = key

    url = f"{BING_API_BASE}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        # Bing API wraps all responses in a {"d": ...} envelope — unwrap it
        if isinstance(data, dict) and "d" in data:
            data = data["d"]
        return data
    except requests.RequestException as e:
        print(f"Bing API error ({endpoint}): {e}")
        return None


def get_sites(api_key: str = None) -> list[str]:
    """List all sites verified in Bing Webmaster Tools."""
    result = _make_request("GetUserSites", api_key=api_key)
    if result is None:
        return []
    # Result is a list of site objects
    if isinstance(result, list):
        return [site.get("Url", "") for site in result if isinstance(site, dict)]
    return []


def fetch_query_stats(site_url: str, api_key: str = None) -> pd.DataFrame:
    """
    Fetch keyword/query traffic stats from Bing.
    Returns clicks, impressions, position data similar to GSC.
    """
    result = _make_request(
        "GetQueryStats",
        params={"siteUrl": site_url},
        api_key=api_key,
    )
    if not result or not isinstance(result, list):
        return pd.DataFrame(columns=["query", "impressions", "clicks", "position", "date"])

    data = []
    for row in result:
        data.append({
            "query": row.get("Query", ""),
            "impressions": row.get("Impressions", 0),
            "clicks": row.get("Clicks", 0),
            "position": round(row.get("AvgClickPosition", 0), 1) if row.get("AvgClickPosition") else 0,
            "date": row.get("Date", ""),
        })

    df = pd.DataFrame(data)
    if not df.empty:
        # Aggregate by query (data comes as daily rows)
        agg = df.groupby("query").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            position=("position", "mean"),
        ).reset_index()
        agg["position"] = agg["position"].round(1)
        agg["ctr"] = (agg["clicks"] / agg["impressions"] * 100).round(2).fillna(0)
        agg = agg.sort_values("clicks", ascending=False).reset_index(drop=True)
        return agg

    return df


def fetch_page_stats(site_url: str, api_key: str = None) -> pd.DataFrame:
    """Fetch per-page traffic stats from Bing."""
    result = _make_request(
        "GetPageStats",
        params={"siteUrl": site_url},
        api_key=api_key,
    )
    if not result or not isinstance(result, list):
        return pd.DataFrame(columns=["page", "impressions", "clicks"])

    data = []
    for row in result:
        data.append({
            "page": row.get("Query", ""),  # Bing uses "Query" for the URL here
            "impressions": row.get("Impressions", 0),
            "clicks": row.get("Clicks", 0),
        })

    df = pd.DataFrame(data)
    if not df.empty:
        agg = df.groupby("page").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
        ).reset_index()
        agg = agg.sort_values("clicks", ascending=False).reset_index(drop=True)
        return agg

    return df


def fetch_crawl_stats(site_url: str, api_key: str = None) -> dict:
    """Fetch crawl statistics from Bing."""
    result = _make_request(
        "GetCrawlStats",
        params={"siteUrl": site_url},
        api_key=api_key,
    )
    if not result or not isinstance(result, list):
        return {"pages_crawled": 0, "crawl_errors": 0, "data": []}

    total_crawled = sum(r.get("CrawledPages", 0) for r in result)
    total_errors = sum(
        r.get("HttpStatus4xx", 0) + r.get("HttpStatus5xx", 0)
        for r in result
    )

    return {
        "pages_crawled": total_crawled,
        "crawl_errors": total_errors,
        "data": result[-7:] if len(result) > 7 else result,  # Last 7 days
    }


def fetch_backlinks(site_url: str, api_key: str = None) -> pd.DataFrame:
    """Fetch inbound link data from Bing."""
    result = _make_request(
        "GetLinkCounts",
        params={"siteUrl": site_url},
        api_key=api_key,
    )
    if not result:
        return pd.DataFrame(columns=["url", "link_count"])

    # GetLinkCounts returns the overall count
    # For detailed backlinks, use GetUrlLinks
    if isinstance(result, (int, float)):
        return pd.DataFrame([{"metric": "total_backlinks", "count": result}])

    return pd.DataFrame([{"metric": "total_backlinks", "count": 0}])


def collect_all(site_url: str, api_key: str = None) -> dict:
    """
    Collect all Bing Webmaster data for a site. Returns a structured dict.
    """
    queries = fetch_query_stats(site_url, api_key)
    pages = fetch_page_stats(site_url, api_key)
    crawl = fetch_crawl_stats(site_url, api_key)
    backlinks = fetch_backlinks(site_url, api_key)

    return {
        "queries": queries,
        "pages": pages,
        "crawl_stats": crawl,
        "backlinks": backlinks,
        "summary": {
            "total_clicks": int(queries["clicks"].sum()) if not queries.empty else 0,
            "total_impressions": int(queries["impressions"].sum()) if not queries.empty else 0,
            "total_queries": len(queries),
            "pages_crawled": crawl.get("pages_crawled", 0),
            "crawl_errors": crawl.get("crawl_errors", 0),
        },
    }
