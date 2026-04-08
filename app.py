"""
app.py — SEO/AEO Analyzer Tool (Streamlit UI)

A comprehensive site analysis tool with two modes:
1. Client Mode — Uses GSC, GA4, GBP, and Bing Webmaster data
2. Prospect/Competitor Mode — Crawls public data for competitive analysis

Run with:  python -m streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd

from config import GEMINI_API_KEY, BING_API_KEY

# ============================================================
# Page Config
# ============================================================
st.set_page_config(
    page_title="SEO/AEO Analyzer — Xpress Promotions Inc",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# CSS — Xpress Promotions Inc Brand Theme
# Primary: #AD1F21 (deep red), Dark: #1A1A1A, Accent: #D4443E
# ============================================================
_LOGO_URL = "https://lirp.cdn-website.com/0955e44c/dms3rep/multi/opt/XpressPromotion-Springfield-VA-logo-1920w.png"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
    }}
    .brand-bar {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }}
    .brand-bar img {{
        height: 52px;
        object-fit: contain;
    }}
    .main-header {{
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #AD1F21 0%, #D4443E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }}
    .sub-header {{
        font-size: 1.05rem;
        color: #888;
        margin-bottom: 1.5rem;
    }}
    .mode-card {{
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s;
    }}
    .mode-card:hover {{
        border-color: #AD1F21;
        box-shadow: 0 4px 12px rgba(173, 31, 33, 0.15);
    }}
    .mode-card.active {{
        border-color: #AD1F21;
        background: #fef2f2;
    }}
    .status-banner {{
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }}
    .status-success {{
        background: #e8f5e9;
        border-left: 4px solid #43a047;
        color: #2e7d32;
    }}
    .status-info {{
        background: #fef2f2;
        border-left: 4px solid #AD1F21;
        color: #7f1516;
    }}
    .data-source-tag {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
    }}
    .tag-gsc {{ background: #e8f5e9; color: #2e7d32; }}
    .tag-ga4 {{ background: #fff3e0; color: #e65100; }}
    .tag-gbp {{ background: #e3f2fd; color: #1565c0; }}
    .tag-bing {{ background: #fce4ec; color: #c62828; }}
    .tag-crawl {{ background: #f3e5f5; color: #6a1b9a; }}
    .metric-card {{
        background: linear-gradient(135deg, #AD1F21 0%, #D4443E 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
        text-align: center;
    }}
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
    }}
    .metric-label {{
        font-size: 0.85rem;
        opacity: 0.9;
    }}

    /* Report table styling */
    .stMarkdown table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 0.85rem;
        margin: 1rem 0;
    }}
    .stMarkdown thead th {{
        background: linear-gradient(135deg, #AD1F21 0%, #8a1819 100%);
        color: white;
        padding: 0.6rem 0.75rem;
        text-align: left;
        font-weight: 600;
        white-space: normal;
        word-break: break-word;
        border: 1px solid #8a1819;
        overflow: hidden;
    }}
    .stMarkdown tbody td {{
        padding: 0.5rem 0.75rem;
        border: 1px solid #e0e0e0;
        vertical-align: top;
        word-break: break-all;
        overflow-wrap: break-word;
        hyphens: auto;
        max-width: 250px;
        overflow: hidden;
    }}
    .stMarkdown tbody tr:nth-child(even) {{
        background-color: rgba(173, 31, 33, 0.04);
    }}
    .stMarkdown tbody tr:hover {{
        background-color: rgba(173, 31, 33, 0.08);
    }}

    /* Streamlit button overrides */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #AD1F21 0%, #D4443E 100%) !important;
        border: none !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #8a1819 0%, #AD1F21 100%) !important;
    }}

    /* Make table container horizontally scrollable on overflow */
    .stMarkdown div[data-testid="stMarkdownContainer"] {{
        overflow-x: auto;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Header — Xpress Promotions Inc Branding
# ============================================================
st.markdown(
    f'<div class="brand-bar">'
    f'<img src="{_LOGO_URL}" alt="Xpress Promotions Inc">'
    f'<div class="main-header">SEO/AEO Analyzer</div>'
    f'</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Comprehensive site analysis powered by Gemini AI — '
    'using data from Google Search Console, GA4, Google Business Profile, and Bing Webmaster Tools</div>',
    unsafe_allow_html=True,
)

# ============================================================
# Sidebar — API Keys & Settings
# ============================================================
with st.sidebar:
    st.header("⚙️ Settings")

    # Gemini API Key
    env_gemini = GEMINI_API_KEY
    if env_gemini:
        gemini_key = env_gemini
        st.success("✅ Gemini API key loaded from .env")
    else:
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Set GEMINI_API_KEY in .env or enter here.",
        )

    st.markdown("---")

    # Bing API Key
    env_bing = BING_API_KEY
    if env_bing:
        bing_key = env_bing
        st.success("✅ Bing API key loaded from .env")
    else:
        bing_key = st.text_input(
            "Bing Webmaster API Key",
            type="password",
            help="Set BING_API_KEY in .env or enter here.",
        )

    st.markdown("---")

    if st.button("🔄 Refresh Connections", use_container_width=True,
                 help="Clear cached data and re-check all API connections"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    st.caption(
        "🔒 **Read-Only Mode** — This tool only reads data. "
        "No modifications are made to any platform."
    )

# ============================================================
# Mode Selector
# ============================================================
st.markdown("---")

col_mode1, col_mode2 = st.columns(2)

with col_mode1:
    client_selected = st.button(
        "👤 Client Analysis",
        use_container_width=True,
        help="Analyze a site you manage — pulls data from GSC, GA4, GBP, and Bing",
        type="primary" if st.session_state.get("mode") == "client" else "secondary",
    )

with col_mode2:
    prospect_selected = st.button(
        "🔍 Prospect / Competitor Analysis",
        use_container_width=True,
        help="Analyze any site using publicly available data",
        type="primary" if st.session_state.get("mode") == "prospect" else "secondary",
    )

if client_selected:
    st.session_state["mode"] = "client"
    # Clear ALL report state when switching modes to prevent bleed
    st.session_state.pop("report", None)
    st.session_state.pop("client_report", None)
    st.session_state.pop("report_filename", None)
    st.rerun()
if prospect_selected:
    st.session_state["mode"] = "prospect"
    st.session_state.pop("report", None)
    st.session_state.pop("client_report", None)
    st.session_state.pop("report_filename", None)
    st.rerun()

mode = st.session_state.get("mode", None)

if not mode:
    st.info("👆 Select an analysis mode to get started.")
    st.markdown("""
    | | Client Analysis | Prospect/Competitor |
    |---|---|---|
    | **Data Sources** | GSC, GA4, GBP, Bing | Public crawl data |
    | **Best For** | Existing clients | New leads, competitors |
    | **Depth** | Full data-driven analysis | Technical + content audit |
    | **Requires Auth** | Yes (Google OAuth) | No |
    """)
    st.stop()

# ============================================================
# CLIENT MODE
# ============================================================
if mode == "client":
    st.markdown(
        '<div class="status-banner status-info">'
        '👤 <strong>Client Mode</strong> — Connect your platforms to run a full analysis. '
        'Data sources: '
        '<span class="data-source-tag tag-gsc">GSC</span>'
        '<span class="data-source-tag tag-bing">Bing</span>'
        '<span class="data-source-tag tag-crawl">Site Crawl</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # --- Authentication ---
    from auth import get_credentials

    @st.cache_resource(show_spinner="Authenticating with Google...")
    def authenticate():
        return get_credentials()

    try:
        creds = authenticate()
        st.success("✅ Google authenticated!")
    except FileNotFoundError as e:
        st.error(f"❌ {e}")
        st.info("💡 Copy your `credentials.json` to the seo-aeo-app folder.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Authentication failed: {e}")
        st.stop()

    # --- GSC Property Selection ---
    st.markdown("### 📊 Select Properties")

    from collectors.gsc import list_properties as list_gsc_props

    @st.cache_data(show_spinner="Loading GSC properties...", ttl=300)
    def get_gsc_properties(_creds):
        return list_gsc_props(_creds)

    gsc_properties = get_gsc_properties(creds)

    if not gsc_properties:
        st.warning("No Search Console properties found.")
        selected_gsc = None
    else:
        gsc_urls = [p["siteUrl"] for p in gsc_properties]
        selected_gsc = st.selectbox(
            "Search Console Property:",
            options=gsc_urls,
            key="gsc_select",
        )


    # --- Bing Site Selection (dropdown from API) ---
    from collectors.bing import get_sites as get_bing_sites

    @st.cache_data(show_spinner="Loading Bing sites...", ttl=300)
    def fetch_bing_sites(api_key):
        return get_bing_sites(api_key)

    if bing_key:
        bing_sites = fetch_bing_sites(bing_key)
        if bing_sites:
            bing_site_url = st.selectbox(
                "Bing Webmaster Site:",
                options=["(Skip Bing)"] + bing_sites,
                key="bing_select",
            )
            if bing_site_url == "(Skip Bing)":
                bing_site_url = None
        else:
            # Fallback to text input when API doesn't list sites
            default_bing = ""
            if selected_gsc:
                default_bing = selected_gsc.replace("sc-domain:", "https://") if selected_gsc.startswith("sc-domain:") else selected_gsc
            bing_site_url = st.text_input(
                "Bing Webmaster Site URL:",
                value=default_bing,
                help="Enter the URL as it appears in Bing Webmaster Tools",
                key="bing_site",
            )
    else:
        st.caption("ℹ️ Add Bing API key in sidebar to include Bing data")
        bing_site_url = None

    # --- Options ---
    with st.expander("⚙️ Analysis Options"):
        include_crawl = st.checkbox(
            "Also crawl the site for technical SEO data",
            value=True,
            help="Adds heading analysis, schema audit, and page-level data",
        )
        crawl_limit = st.slider("Max pages to crawl", 10, 100, 30, step=10) if include_crawl else 0

    # --- Run Analysis ---
    st.markdown("---")

    if st.button("🚀 Run Full Analysis", type="primary", use_container_width=True):
        if not gemini_key:
            st.error("❌ Please provide a Gemini API key in the sidebar.")
            st.stop()

        # Collect data from all sources
        collected = {}

        # GSC
        if selected_gsc:
            with st.spinner("📊 Collecting GSC data..."):
                from collectors.gsc import collect_all as gsc_collect
                try:
                    collected["gsc"] = gsc_collect(creds, selected_gsc)
                    st.success(f"✅ GSC: {collected['gsc']['summary']['total_queries']} queries, "
                             f"{collected['gsc']['summary']['total_pages']} pages")
                except Exception as e:
                    st.warning(f"⚠️ GSC collection failed: {e}")


        # Bing
        if bing_site_url and bing_key:
            with st.spinner("🔍 Collecting Bing data..."):
                from collectors.bing import collect_all as bing_collect
                try:
                    collected["bing"] = bing_collect(bing_site_url, bing_key)
                    st.success(f"✅ Bing: {collected['bing']['summary']['total_queries']} queries")
                except Exception as e:
                    st.warning(f"⚠️ Bing collection failed: {e}")

        # Site Crawl
        crawl_data = None
        if include_crawl and selected_gsc:
            crawl_url = selected_gsc.replace("sc-domain:", "https://www.")
            if not crawl_url.startswith("http"):
                crawl_url = "https://" + crawl_url

            with st.spinner(f"🕷️ Crawling {crawl_url} (up to {crawl_limit} pages)..."):
                from collectors.crawler import crawl_site
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(current, total, url):
                    progress_bar.progress(min(current / total, 1.0))
                    status_text.caption(f"Crawling: {url}")

                try:
                    crawl_data = crawl_site(crawl_url, max_pages=crawl_limit, progress_callback=update_progress)
                    collected["crawl"] = crawl_data
                    st.success(f"✅ Crawl: {crawl_data['summary']['pages_crawled']} pages analyzed")
                except Exception as e:
                    st.warning(f"⚠️ Crawl failed: {e}")
                finally:
                    progress_bar.empty()
                    status_text.empty()

        # Run Gemini Analysis
        if collected:
            st.markdown("---")
            with st.spinner("🧠 Gemini is analyzing all your data... This may take a minute."):
                from agent.orchestrator import run_client_analysis
                from agent.report import format_report_header, wrap_report, get_report_filename

                try:
                    site_label = selected_gsc or bing_site_url or "Unknown"
                    header = format_report_header(site_label, "client")

                    analysis = run_client_analysis(
                        gsc_data=collected.get("gsc"),
                        bing_data=collected.get("bing"),
                        crawl_data=collected.get("crawl"),
                        api_key=gemini_key,
                    )

                    full_report = wrap_report(header, analysis)
                    st.session_state["report"] = full_report
                    st.session_state["report_filename"] = get_report_filename(site_label)

                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
        else:
            st.warning("⚠️ No data was collected. Please check your connections.")

# ============================================================
# PROSPECT / COMPETITOR MODE
# ============================================================
elif mode == "prospect":
    st.markdown(
        '<div class="status-banner status-info">'
        '🔍 <strong>Prospect/Competitor Mode</strong> — Enter any URL to crawl and analyze. '
        'No platform access needed. '
        '<span class="data-source-tag tag-crawl">Public Crawl</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    target_url = st.text_input(
        "Target Website URL:",
        placeholder="example.com",
        help="Enter the website URL you want to analyze",
        key="prospect_url",
    )

    with st.expander("⚙️ Crawl Options"):
        prospect_crawl_limit = st.slider("Max pages to crawl", 10, 100, 30, step=10, key="prospect_limit")

    if st.button("🚀 Analyze Site", type="primary", use_container_width=True):
        if not target_url:
            st.error("❌ Please enter a URL.")
            st.stop()
        if not gemini_key:
            st.error("❌ Please provide a Gemini API key in the sidebar.")
            st.stop()

        # Crawl the site
        from collectors.crawler import crawl_site

        with st.spinner(f"🕷️ Crawling {target_url} (up to {prospect_crawl_limit} pages)..."):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(current, total, url):
                progress_bar.progress(min(current / total, 1.0))
                status_text.caption(f"Crawling: {url}")

            try:
                crawl_data = crawl_site(
                    target_url,
                    max_pages=prospect_crawl_limit,
                    progress_callback=update_progress,
                )
            except Exception as e:
                st.error(f"❌ Crawl failed: {e}")
                st.stop()
            finally:
                progress_bar.empty()
                status_text.empty()

        # Show crawl summary
        summary = crawl_data["summary"]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pages Crawled", summary["pages_crawled"])
        with col2:
            st.metric("Avg Words/Page", summary["avg_word_count"])
        with col3:
            st.metric("Avg Load Time", f"{summary['avg_load_time']}s")
        with col4:
            st.metric("Schema Types", len(summary["schema_types_found"]))

        # Run Gemini Analysis
        with st.spinner("🧠 Gemini is analyzing the crawled data... This may take a minute."):
            from agent.orchestrator import run_prospect_analysis
            from agent.report import format_report_header, wrap_report, get_report_filename

            try:
                header = format_report_header(target_url, "prospect")
                analysis = run_prospect_analysis(
                    crawl_data=crawl_data,
                    api_key=gemini_key,
                )

                full_report = wrap_report(header, analysis)
                st.session_state["report"] = full_report
                st.session_state["report_filename"] = get_report_filename(target_url)

            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")

# ============================================================
# REPORT POST-PROCESSING
# ============================================================


import io
import re
import markdown
from xhtml2pdf import pisa

# ============================================================
# PDF Emoji Support — Register symbol font for emoji rendering
# ============================================================
_SYMBOL_FONT_REGISTERED = False
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    _sys_root = os.environ.get('SYSTEMROOT', os.environ.get('WINDIR', r'C:\Windows'))
    _symbol_path = os.path.join(_sys_root, 'Fonts', 'seguisym.ttf')
    if os.path.exists(_symbol_path):
        pdfmetrics.registerFont(TTFont('SegoeSymbol', _symbol_path))
        _SYMBOL_FONT_REGISTERED = True
except Exception:
    pass

# Emoji → Unicode symbol mapping (symbols that Segoe UI Symbol supports)
_EMOJI_SYMBOL_MAP = {
    '✅': ('\u2713', '#2e7d32'),   # ✓ green
    '⚠️': ('\u26A0', '#f57c00'),  # ⚠ orange
    '❌': ('\u2717', '#c62828'),   # ✗ red
    '📊': ('\u25A3', '#AD1F21'),  # ▣
    '📈': ('\u25B2', '#2e7d32'),  # ▲ green
    '📉': ('\u25BC', '#c62828'),  # ▼ red
    '🔍': ('\u2295', '#555'),     # ⊕
    '🎯': ('\u25CE', '#AD1F21'),  # ◎
    '🚀': ('\u25BA', '#AD1F21'),  # ►
    '💡': ('\u25C7', '#f9a825'),  # ◇
    '⭐': ('\u2605', '#f9a825'),  # ★ gold
    '🏆': ('\u2605', '#f9a825'),  # ★ gold
    '📋': ('\u25A4', '#555'),     # ▤
    '📌': ('\u25C6', '#AD1F21'),  # ◆
    '🔒': ('\u25C8', '#555'),     # ◈
    '🔑': ('\u25C7', '#555'),     # ◇
    '💰': ('\u25C6', '#2e7d32'),  # ◆ green
    '📤': ('\u25B3', '#555'),     # △
    '📥': ('\u25BD', '#555'),     # ▽
    '🤝': ('\u25C7', '#AD1F21'),  # ◇
    '🔄': ('\u21BB', '#555'),     # ↻
    '⚙️': ('\u2699', '#555'),     # ⚙
    '🔬': ('\u25C9', '#AD1F21'),  # ◉
    '👤': ('\u25C9', '#555'),     # ◉
    '🌐': ('\u2295', '#555'),     # ⊕
    '✨': ('\u2726', '#f9a825'),  # ✦
    '🏥': ('\u271A', '#c62828'),  # ✚
    '📱': ('\u25A7', '#555'),     # ◧
    '💻': ('\u25A3', '#555'),     # ▣
    '🗺️': ('\u25A6', '#555'),    # ▦
    '📝': ('\u25A4', '#555'),     # ▤
    '🤖': ('\u25CE', '#555'),     # ◎
    '🔧': ('\u2699', '#555'),     # ⚙
    '🗓️': ('\u25A4', '#555'),    # ▤
    '📍': ('\u25C6', '#c62828'),  # ◆ red
    '🟢': ('\u25CF', '#2e7d32'),  # ● green
    '🟡': ('\u25CF', '#f9a825'),  # ● yellow
    '🔴': ('\u25CF', '#c62828'),  # ● red
    '📄': ('\u25A4', '#555'),     # ▤
    '🕷️': ('\u25CE', '#555'),    # ◎
    '🧠': ('\u25C9', '#AD1F21'),  # ◉
}


def _convert_emojis_for_pdf(html: str) -> str:
    """Convert emoji characters to colored Unicode symbols for PDF rendering.

    Uses Segoe UI Symbol font (registered above) for symbol glyphs,
    with color-coded styling so the PDF looks professional.
    Falls back to plain symbols if the font isn't available.
    """
    for emoji, (symbol, color) in _EMOJI_SYMBOL_MAP.items():
        if emoji in html:
            if _SYMBOL_FONT_REGISTERED:
                html = html.replace(
                    emoji,
                    f'<span style="font-family:SegoeSymbol;color:{color};">{symbol}</span>'
                )
            else:
                html = html.replace(emoji, symbol)

    # Catch-all: strip any remaining unmapped emoji chars
    html = re.sub(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
        r'\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF'
        r'\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF'
        r'\U0000FE0F]+',
        '', html
    )
    return html


def _sanitize_report_tables(md_text: str) -> str:
    """Clean up malformed markdown tables from Gemini output.

    Fixes common issues:
    - Empty table rows (just pipes and spaces)
    - Rows with inconsistent column counts
    - Separator rows that aren't valid (must be |---|---|)
    - Tables so large they crash the renderer
    """
    lines = md_text.split('\n')
    cleaned = []
    in_table = False
    table_col_count = 0
    table_lines = []
    empty_row_streak = 0

    def _flush_table(tbl_lines, col_count):
        """Validate and emit a cleaned table."""
        if len(tbl_lines) < 2:
            return tbl_lines  # Not a real table

        valid = []
        for i, line in enumerate(tbl_lines):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]

            # Skip fully empty rows
            if all(c == '' or set(c) <= {'-', ':', ' '} for c in cells) and i > 1:
                continue

            # Pad or trim to match column count
            if len(cells) < col_count:
                cells += [''] * (col_count - len(cells))
            elif len(cells) > col_count:
                cells = cells[:col_count]

            valid.append('| ' + ' | '.join(cells) + ' |')

        # Cap at 50 data rows to avoid renderer overload
        if len(valid) > 52:  # header + separator + 50 rows
            valid = valid[:52]
            valid.append('')
            valid.append('*... table truncated for readability (showing first 50 rows) ...*')

        return valid

    for line in lines:
        stripped = line.strip()

        # Detect table start: line that starts and ends with |
        if stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
                # Count columns from header
                cells = [c.strip() for c in stripped.strip('|').split('|')]
                table_col_count = len(cells)
                empty_row_streak = 0

            # Check for empty rows
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            has_content = any(c and not set(c) <= {'-', ':', ' '} for c in cells)

            if not has_content and len(table_lines) > 1:  # Allow separator row
                empty_row_streak += 1
                if empty_row_streak > 2:
                    continue  # Skip excessive empty rows
            else:
                empty_row_streak = 0

            table_lines.append(line)
        else:
            if in_table:
                # Table ended — flush it
                cleaned.extend(_flush_table(table_lines, table_col_count))
                in_table = False
                table_lines = []
                table_col_count = 0
            cleaned.append(line)

    # Flush any remaining table
    if in_table:
        cleaned.extend(_flush_table(table_lines, table_col_count))

    return '\n'.join(cleaned)


# ============================================================
# REPORT DISPLAY (shared between both modes)
# ============================================================
if "report" in st.session_state:
    st.markdown("---")
    st.markdown("## 📋 Analysis Report")

    # Sanitize tables before display
    report_md = _sanitize_report_tables(st.session_state["report"])
    st.session_state["report"] = report_md  # Update stored version

    st.markdown(report_md)

    # Convert markdown to HTML, then convert emojis to styled symbols for PDF
    report_html_body = markdown.markdown(
        report_md,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    report_html_body = _convert_emojis_for_pdf(report_html_body)
    report_filename_base = st.session_state.get(
        "report_filename", "seo_aeo_report.md"
    ).replace(".md", "")

    def _fix_tables_for_pdf(html: str) -> str:
        """Post-process HTML tables for xhtml2pdf compatibility.
        
        xhtml2pdf has limited CSS support, so we:
        1. Analyze actual cell content to assign proportional column widths
        2. Insert zero-width spaces into long words/URLs so they can wrap
        3. Add inline styles on each cell for word-wrapping
        """

        def _break_long_text(text: str) -> str:
            """Insert zero-width spaces into long words and URLs."""
            zwsp = '\u200b'

            # Break URLs at natural break points
            def _break_url(m):
                url = m.group(0)
                broken = ''
                for ch in url:
                    broken += ch
                    if ch in ('/', '-', '.', '=', '&', '_', '?'):
                        broken += zwsp
                return broken

            text = re.sub(r'https?://[^\s<>"]+', _break_url, text)

            # Also break any remaining long words (30+ chars without spaces)
            def _break_word(m):
                word = m.group(0)
                result = ''
                for i, ch in enumerate(word):
                    result += ch
                    if (i + 1) % 25 == 0:
                        result += zwsp
                return result

            text = re.sub(r'\S{30,}', _break_word, text)
            return text

        def _get_text_length(html_content: str) -> int:
            """Get approximate visible text length from HTML content."""
            clean = re.sub(r'<[^>]+>', '', html_content)
            clean = clean.replace('\u200b', '').strip()
            return len(clean)

        def _process_table(match):
            full_table = match.group(0)

            # Extract all rows
            rows = re.findall(r'<tr>(.*?)</tr>', full_table, re.DOTALL)
            if not rows:
                return full_table

            # Count columns from header row
            first_row = rows[0]
            headers = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', first_row, re.DOTALL)
            col_count = len(headers)
            if col_count == 0:
                return full_table

            # Only add colgroup for tables with 5 or fewer columns.
            # Wide tables (6+) crash xhtml2pdf when percentage widths
            # make columns narrower than their cell padding.
            if col_count <= 5:
                # Calculate max content length per column across all rows
                col_max_len = [0] * col_count
                for row_html in rows:
                    cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row_html, re.DOTALL)
                    for i, cell in enumerate(cells):
                        if i < col_count:
                            length = _get_text_length(cell)
                            col_max_len[i] = max(col_max_len[i], length)

                # Give each column a minimum weight, then distribute proportionally
                min_weight = 5
                col_weights = [max(length, min_weight) for length in col_max_len]
                total_weight = sum(col_weights)

                # Calculate percentages with a reasonable minimum
                min_pct = max(10, 100 // col_count)
                widths = []
                for w in col_weights:
                    pct = max((w / total_weight) * 100, min_pct)
                    widths.append(pct)

                # Normalize to 100%
                total_pct = sum(widths)
                widths = [round(w / total_pct * 100, 1) for w in widths]

                colgroup = '<colgroup>' + ''.join(
                    f'<col style="width:{w}%"/>' for w in widths
                ) + '</colgroup>'

                # Insert colgroup right after <table...>
                full_table = re.sub(
                    r'(<table[^>]*>)',
                    r'\1' + colgroup,
                    full_table,
                    count=1,
                )

            # Reduce padding for wide tables to prevent negative availWidth
            cell_padding = "2px 3px" if col_count >= 6 else "4px 5px"
            th_padding = "3px 4px" if col_count >= 6 else "5px 6px"

            # Fix <td> cells: break long text + add inline styles
            def _fix_td(m):
                content = m.group(1)
                content = _break_long_text(content)
                return f'<td style="word-wrap:break-word;overflow:hidden;vertical-align:top;padding:{cell_padding};">{content}</td>'

            full_table = re.sub(r'<td[^>]*>(.*?)</td>', _fix_td, full_table, flags=re.DOTALL)

            # Fix <th> cells
            def _fix_th(m):
                content = m.group(1)
                content = _break_long_text(content)
                return f'<th style="word-wrap:break-word;overflow:hidden;vertical-align:top;padding:{th_padding};">{content}</th>'

            full_table = re.sub(r'<th[^>]*>(.*?)</th>', _fix_th, full_table, flags=re.DOTALL)

            return full_table

        # Process each table
        html = re.sub(r'<table[^>]*>.*?</table>', _process_table, html, flags=re.DOTALL)

        return html

    report_html_body = _fix_tables_for_pdf(report_html_body)

    pdf_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {{
        size: letter landscape;
        margin: 1.5cm 1.5cm;
    }}
    body {{
        font-family: Helvetica, Arial, sans-serif;
        font-size: 9pt;
        color: #1a1a2e;
        line-height: 1.5;
    }}
    h1 {{
        color: #AD1F21;
        font-size: 18pt;
        border-bottom: 3px solid #AD1F21;
        padding-bottom: 6px;
        margin-top: 18px;
    }}
    h2 {{
        color: #8a1819;
        font-size: 14pt;
        margin-top: 18px;
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 4px;
    }}
    h3 {{
        color: #333;
        font-size: 11pt;
        margin-top: 12px;
    }}
    h4 {{
        color: #555;
        font-size: 10pt;
        margin-top: 10px;
    }}
    p {{
        margin: 5px 0;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
        font-size: 8pt;
        table-layout: fixed;
    }}
    th {{
        background-color: #AD1F21;
        color: white;
        padding: 5px 6px;
        text-align: left;
        font-weight: bold;
    }}
    td {{
        border: 1px solid #ddd;
        padding: 4px 6px;
        text-align: left;
    }}
    ul, ol {{
        padding-left: 18px;
        margin: 5px 0;
    }}
    li {{
        margin-bottom: 2px;
    }}
    code {{
        background-color: #f0f2ff;
        padding: 1px 3px;
        font-family: 'Courier New', monospace;
        font-size: 8pt;
    }}
    hr {{
        border: none;
        border-top: 2px solid #e9ecef;
        margin: 14px 0;
    }}
    strong {{
        color: #1a1a2e;
    }}
    a {{
        color: #AD1F21;
        text-decoration: none;
    }}
    .footer {{
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid #ccc;
        font-size: 8pt;
        color: #999;
        text-align: center;
    }}
</style>
</head>
<body>
{report_html_body}
<div class="footer">
    Generated by SEO/AEO Analyzer &mdash; Data sourced from Google Search Console, GA4, GBP, and Bing Webmaster Tools
</div>
</body>
</html>"""

    # Generate PDF in memory
    def generate_pdf(html_content):
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=pdf_buffer)
        if pisa_status.err:
            return None
        return pdf_buffer.getvalue()

    try:
        pdf_bytes = generate_pdf(pdf_html)
    except Exception as e:
        import traceback
        traceback.print_exc()
        pdf_bytes = None

    # Export buttons — Row 1: Downloads
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if pdf_bytes:
            st.download_button(
                label="📥 Download Report (PDF)",
                data=pdf_bytes,
                file_name=f"{report_filename_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.warning("⚠️ PDF generation failed — download as Markdown instead.")
    with col_dl2:
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=report_md,
            file_name=f"{report_filename_base}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # Export buttons — Row 2: Actions
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("📤 Generate Client Report", use_container_width=True,
                     help="Create a polished, client-facing version of this report"):
            if not gemini_key:
                st.error("❌ Gemini API key required to generate client report.")
            else:
                with st.spinner("✨ Generating client-facing report..."):
                    from agent.orchestrator import generate_client_facing_report

                    try:
                        site_label = st.session_state.get("report_filename", "site")
                        client_report_md = generate_client_facing_report(
                            internal_report=report_md,
                            site_url=site_label,
                            api_key=gemini_key,
                        )
                        st.session_state["client_report"] = client_report_md
                    except Exception as e:
                        st.error(f"❌ Client report generation failed: {e}")

    with col_act2:
        if st.button("🔄 Run New Analysis", use_container_width=True):
            st.session_state.pop("report", None)
            st.session_state.pop("client_report", None)
            st.session_state.pop("mode", None)
            st.rerun()

    # Client-facing report display & download
    if "client_report" in st.session_state:
        st.markdown("---")
        st.markdown("## 📤 Client-Facing Report")
        st.markdown(st.session_state["client_report"])

        # Generate PDF of client report with emoji support
        client_md_clean = _sanitize_report_tables(st.session_state["client_report"])
        client_report_html_body = markdown.markdown(
            client_md_clean,
            extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        )
        client_report_html_body = _convert_emojis_for_pdf(client_report_html_body)
        client_report_html_body = _fix_tables_for_pdf(client_report_html_body)

        # Encode non-ASCII to XML char refs (symbol chars inside spans become entities)
        client_report_html_body = client_report_html_body.encode('ascii', 'xmlcharrefreplace').decode('ascii')

        client_pdf_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {{
        size: letter portrait;
        margin: 2cm 2cm;
    }}
    body {{
        font-family: Helvetica, Arial, sans-serif;
        font-size: 10pt;
        color: #1a1a2e;
        line-height: 1.6;
    }}
    h1 {{
        color: #AD1F21;
        font-size: 20pt;
        border-bottom: 3px solid #AD1F21;
        padding-bottom: 8px;
        margin-top: 20px;
    }}
    h2 {{
        color: #8a1819;
        font-size: 15pt;
        margin-top: 20px;
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 5px;
    }}
    h3 {{
        color: #333;
        font-size: 12pt;
        margin-top: 14px;
    }}
    p {{
        margin: 6px 0;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
        font-size: 9pt;
        table-layout: fixed;
    }}
    th {{
        background-color: #AD1F21;
        color: white;
        padding: 6px 8px;
        text-align: left;
        font-weight: bold;
    }}
    td {{
        border: 1px solid #ddd;
        padding: 5px 8px;
        text-align: left;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}
    ul, ol {{
        padding-left: 20px;
        margin: 6px 0;
    }}
    li {{
        margin-bottom: 3px;
    }}
    strong {{
        color: #1a1a2e;
    }}
    a {{
        color: #AD1F21;
    }}
    .footer {{
        margin-top: 40px;
        padding-top: 12px;
        border-top: 1px solid #ccc;
        font-size: 8pt;
        color: #999;
        text-align: center;
    }}
</style>
</head>
<body>
{client_report_html_body}
<div class="footer">
    Prepared by Xpress Promotions Inc &mdash; Confidential
</div>
</body>
</html>"""

        try:
            client_pdf_buffer = io.BytesIO()
            pisa_status = pisa.CreatePDF(
                io.StringIO(client_pdf_html), dest=client_pdf_buffer
            )
            client_pdf_bytes = client_pdf_buffer.getvalue()
            # xhtml2pdf reports "errors" for non-fatal warnings (font issues, etc.)
            # Accept the PDF as long as we got valid bytes
            if len(client_pdf_bytes) < 100:
                print(f"[CLIENT PDF] Generated only {len(client_pdf_bytes)} bytes")
                client_pdf_bytes = None
        except Exception as e:
            import traceback
            print(f"[CLIENT PDF] Exception: {e}")
            traceback.print_exc()
            client_pdf_bytes = None

        col_cl1, col_cl2 = st.columns(2)
        with col_cl1:
            if client_pdf_bytes:
                st.download_button(
                    label="📥 Download Client Report (PDF)",
                    data=client_pdf_bytes,
                    file_name=f"{report_filename_base}_client.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.warning("⚠️ Client PDF failed — use Markdown instead.")
        with col_cl2:
            st.download_button(
                label="📥 Download Client Report (Markdown)",
                data=st.session_state["client_report"],
                file_name=f"{report_filename_base}_client.md",
                mime="text/markdown",
                use_container_width=True,
            )

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption(
    "🔒 **Read-Only Mode** — This tool only reads data from connected platforms. "
    "No modifications are made. Gemini AI is used for analysis only."
)
