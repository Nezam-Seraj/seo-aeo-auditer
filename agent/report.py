"""
report.py — Report Formatting & Export

Formats analysis results for display and export.
"""

from datetime import datetime


def format_report_header(site_url: str, mode: str) -> str:
    """Generate the report header."""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    mode_label = "Client Analysis" if mode == "client" else "Prospect/Competitor Analysis"

    return f"""# 🔍 SEO/AEO Site Analysis Report
**Site:** {site_url}  
**Mode:** {mode_label}  
**Generated:** {timestamp}  
**Data Window:** Last 90 days

---

"""


def wrap_report(header: str, analysis: str) -> str:
    """Combine header with analysis content."""
    return header + analysis


def get_report_filename(site_url: str) -> str:
    """Generate a clean filename for the report export."""
    # Clean the URL for filename use
    clean = site_url.replace("https://", "").replace("http://", "")
    clean = clean.replace("/", "_").replace(".", "_").replace(":", "")
    clean = clean.strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"seo_aeo_report_{clean}_{timestamp}.md"
