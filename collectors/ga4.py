"""
ga4.py — Google Analytics 4 Data Collector (Read-Only)

Fetches traffic, landing page, and source/medium data from GA4
using the Google Analytics Data API.
"""

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy,
)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import DEFAULT_DAYS


def _get_admin_service(creds: Credentials):
    """Build the GA4 Admin API service to list properties."""
    return build("analyticsadmin", "v1beta", credentials=creds)


def _get_data_client(creds: Credentials) -> BetaAnalyticsDataClient:
    """Build the GA4 Data API client."""
    return BetaAnalyticsDataClient(credentials=creds)


def list_properties(creds: Credentials) -> list[dict]:
    """
    List all GA4 properties accessible to the authenticated account.
    Returns a list of dicts with 'name', 'displayName', and 'propertyId'.
    """
    service = _get_admin_service(creds)
    try:
        # List all accounts first
        accounts_response = service.accounts().list().execute()
        accounts = accounts_response.get("accounts", [])

        properties = []
        for account in accounts:
            account_name = account["name"]  # e.g. "accounts/123456"
            props_response = service.properties().list(
                filter=f"parent:{account_name}"
            ).execute()
            for prop in props_response.get("properties", []):
                prop_name = prop["name"]  # e.g. "properties/123456"
                prop_id = prop_name.split("/")[-1]
                properties.append({
                    "name": prop_name,
                    "displayName": prop.get("displayName", ""),
                    "propertyId": prop_id,
                    "industryCategory": prop.get("industryCategory", ""),
                    "timeZone": prop.get("timeZone", ""),
                })
        return properties
    except Exception as e:
        print(f"Warning: Could not list GA4 properties: {e}")
        return []


def _run_report(
    creds: Credentials,
    property_id: str,
    dimensions: list[str],
    metrics: list[str],
    days: int = DEFAULT_DAYS,
    limit: int = 100,
) -> pd.DataFrame:
    """Run a GA4 report and return as DataFrame."""
    client = _get_data_client(creds)

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name=metrics[0]), desc=True)],
        limit=limit,
    )

    response = client.run_report(request)

    rows = []
    for row in response.rows:
        entry = {}
        for i, dim in enumerate(dimensions):
            entry[dim] = row.dimension_values[i].value
        for i, met in enumerate(metrics):
            val = row.metric_values[i].value
            # Try to convert to number
            try:
                entry[met] = int(val)
            except ValueError:
                try:
                    entry[met] = float(val)
                except ValueError:
                    entry[met] = val
        rows.append(entry)

    return pd.DataFrame(rows)


def fetch_traffic_overview(creds: Credentials, property_id: str, days: int = DEFAULT_DAYS) -> dict:
    """Fetch high-level traffic metrics."""
    client = _get_data_client(creds)

    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
            Metric(name="screenPageViews"),
            Metric(name="engagedSessions"),
        ],
    )

    response = client.run_report(request)

    if not response.rows:
        return {}

    row = response.rows[0]
    metric_names = ["sessions", "totalUsers", "newUsers", "bounceRate",
                    "averageSessionDuration", "screenPageViews", "engagedSessions"]

    result = {}
    for i, name in enumerate(metric_names):
        val = row.metric_values[i].value
        try:
            result[name] = int(val)
        except ValueError:
            try:
                result[name] = round(float(val), 2)
            except ValueError:
                result[name] = val

    return result


def fetch_top_landing_pages(creds: Credentials, property_id: str, days: int = DEFAULT_DAYS) -> pd.DataFrame:
    """Fetch top landing pages by sessions."""
    return _run_report(
        creds, property_id,
        dimensions=["landingPagePlusQueryString"],
        metrics=["sessions", "totalUsers", "bounceRate", "averageSessionDuration"],
        days=days,
        limit=100,
    )


def fetch_traffic_sources(creds: Credentials, property_id: str, days: int = DEFAULT_DAYS) -> pd.DataFrame:
    """Fetch traffic source/medium breakdown."""
    return _run_report(
        creds, property_id,
        dimensions=["sessionSource", "sessionMedium"],
        metrics=["sessions", "totalUsers", "bounceRate"],
        days=days,
        limit=50,
    )


def fetch_top_events(creds: Credentials, property_id: str, days: int = DEFAULT_DAYS) -> pd.DataFrame:
    """Fetch top events (conversions, key actions)."""
    return _run_report(
        creds, property_id,
        dimensions=["eventName"],
        metrics=["eventCount", "totalUsers"],
        days=days,
        limit=30,
    )


def fetch_device_breakdown(creds: Credentials, property_id: str, days: int = DEFAULT_DAYS) -> pd.DataFrame:
    """Fetch device category breakdown."""
    return _run_report(
        creds, property_id,
        dimensions=["deviceCategory"],
        metrics=["sessions", "totalUsers", "bounceRate"],
        days=days,
        limit=10,
    )


def collect_all(creds: Credentials, property_id: str) -> dict:
    """
    Collect all GA4 data for a property. Returns a structured dict.
    """
    traffic = fetch_traffic_overview(creds, property_id)
    landing_pages = fetch_top_landing_pages(creds, property_id)
    sources = fetch_traffic_sources(creds, property_id)
    events = fetch_top_events(creds, property_id)
    devices = fetch_device_breakdown(creds, property_id)

    return {
        "traffic_overview": traffic,
        "landing_pages": landing_pages,
        "traffic_sources": sources,
        "events": events,
        "devices": devices,
    }
