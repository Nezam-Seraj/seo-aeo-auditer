"""
gbp.py — Google Business Profile Data Collector (Read-Only)

Fetches business location info, reviews, and performance insights
from the Google Business Profile (formerly Google My Business) API.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def _get_biz_info_service(creds: Credentials):
    """Build the Business Information API service."""
    return build("mybusinessbusinessinformation", "v1", credentials=creds)


def _get_account_mgmt_service(creds: Credentials):
    """Build the My Business Account Management API service."""
    return build("mybusinessaccountmanagement", "v1", credentials=creds)


def list_accounts(creds: Credentials) -> list[dict]:
    """List all GBP accounts."""
    service = _get_account_mgmt_service(creds)
    try:
        response = service.accounts().list().execute()
        accounts = response.get("accounts", [])
        return [
            {
                "name": acct.get("name", ""),
                "accountName": acct.get("accountName", ""),
                "type": acct.get("type", ""),
            }
            for acct in accounts
        ]
    except Exception as e:
        print(f"Warning: Could not list GBP accounts: {e}")
        return []


def list_locations(creds: Credentials, account_name: str) -> list[dict]:
    """
    List all locations under a GBP account.
    account_name: e.g. 'accounts/123456789'
    """
    service = _get_biz_info_service(creds)
    try:
        response = service.accounts().locations().list(
            parent=account_name,
            readMask="name,title,storefrontAddress,websiteUri,phoneNumbers,categories,metadata",
        ).execute()
        locations = response.get("locations", [])
        results = []
        for loc in locations:
            address = loc.get("storefrontAddress", {})
            address_lines = address.get("addressLines", [])
            results.append({
                "name": loc.get("name", ""),
                "title": loc.get("title", ""),
                "address": ", ".join(address_lines) if address_lines else "",
                "city": address.get("locality", ""),
                "state": address.get("administrativeArea", ""),
                "zipCode": address.get("postalCode", ""),
                "websiteUri": loc.get("websiteUri", ""),
                "phone": loc.get("phoneNumbers", {}).get("primaryPhone", ""),
                "primaryCategory": loc.get("categories", {}).get("primaryCategory", {}).get("displayName", ""),
            })
        return results
    except Exception as e:
        print(f"Warning: Could not list GBP locations: {e}")
        return []


def fetch_reviews(creds: Credentials, location_name: str) -> dict:
    """
    Fetch review summary for a location.
    Uses the My Business API v4 for reviews (v1 doesn't have reviews).
    
    Returns dict with averageRating, totalReviewCount.
    """
    try:
        # The reviews API uses a different endpoint
        service = build("mybusiness", "v4", credentials=creds)
        response = service.accounts().locations().reviews().list(
            parent=location_name,
            pageSize=1,  # We just need summary data
        ).execute()
        return {
            "averageRating": response.get("averageRating", 0),
            "totalReviewCount": response.get("totalReviewCount", 0),
        }
    except Exception as e:
        print(f"Warning: Could not fetch reviews: {e}")
        return {"averageRating": 0, "totalReviewCount": 0}


def collect_all(creds: Credentials) -> dict:
    """
    Collect all GBP data. Returns a structured dict.
    """
    accounts = list_accounts(creds)
    if not accounts:
        return {
            "accounts": [],
            "locations": [],
            "available": False,
            "error": "No GBP accounts found or API not enabled.",
        }

    all_locations = []
    for account in accounts:
        locations = list_locations(creds, account["name"])
        for loc in locations:
            loc["accountName"] = account["accountName"]
            # Try to get reviews for each location
            reviews = fetch_reviews(creds, loc["name"])
            loc["averageRating"] = reviews.get("averageRating", 0)
            loc["totalReviewCount"] = reviews.get("totalReviewCount", 0)
        all_locations.extend(locations)

    return {
        "accounts": accounts,
        "locations": all_locations,
        "available": True,
    }
