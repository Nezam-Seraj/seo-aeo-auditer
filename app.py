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
    page_title="SEO/AEO Analyzer",
    page_icon="🔬",
    layout="wide",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #888;
        margin-bottom: 1.5rem;
    }
    .mode-card {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s;
    }
    .mode-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    .mode-card.active {
        border-color: #667eea;
        background: #f0f2ff;
    }
    .status-banner {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .status-success {
        background: #e8f5e9;
        border-left: 4px solid #43a047;
        color: #2e7d32;
    }
    .status-info {
        background: #e3f2fd;
        border-left: 4px solid #1e88e5;
        color: #1565c0;
    }
    .data-source-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.15rem;
    }
    .tag-gsc { background: #e8f5e9; color: #2e7d32; }
    .tag-ga4 { background: #fff3e0; color: #e65100; }
    .tag-gbp { background: #e3f2fd; color: #1565c0; }
    .tag-bing { background: #fce4ec; color: #c62828; }
    .tag-crawl { background: #f3e5f5; color: #6a1b9a; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }

    /* Report table styling */
    .stMarkdown table {
        width: 100%;
        border-collapse: collapse;
        table-layout: auto;
        font-size: 0.85rem;
        margin: 1rem 0;
    }
    .stMarkdown thead th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.6rem 0.75rem;
        text-align: left;
        font-weight: 600;
        white-space: nowrap;
        border: 1px solid #5a6fd6;
    }
    .stMarkdown tbody td {
        padding: 0.5rem 0.75rem;
        border: 1px solid #e0e0e0;
        vertical-align: top;
        word-wrap: break-word;
        overflow-wrap: break-word;
        min-width: 80px;
    }
    .stMarkdown tbody tr:nth-child(even) {
        background-color: rgba(102, 126, 234, 0.04);
    }
    .stMarkdown tbody tr:hover {
        background-color: rgba(102, 126, 234, 0.08);
    }

    /* Make table container horizontally scrollable on overflow */
    .stMarkdown div[data-testid="stMarkdownContainer"] {
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Header
# ============================================================
st.markdown('<div class="main-header">🔬 SEO/AEO Analyzer</div>', unsafe_allow_html=True)
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
    # Clear any previous report when switching modes
    st.session_state.pop("report", None)
if prospect_selected:
    st.session_state["mode"] = "prospect"
    st.session_state.pop("report", None)

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
# REPORT DISPLAY (shared between both modes)
# ============================================================
if "report" in st.session_state:
    st.markdown("---")
    st.markdown("## 📋 Analysis Report")

    st.markdown(st.session_state["report"])

    # Build styled HTML for PDF conversion
    import io
    import re
    import markdown
    from xhtml2pdf import pisa

    report_md = st.session_state["report"]
    report_html_body = markdown.markdown(
        report_md,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
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

            # Calculate percentages with a minimum of 6% per column
            min_pct = 6
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

            # Fix <td> cells: break long text + add inline styles
            def _fix_td(m):
                content = m.group(1)
                content = _break_long_text(content)
                return f'<td style="word-wrap:break-word;overflow:hidden;vertical-align:top;padding:4px 5px;">{content}</td>'

            full_table = re.sub(r'<td[^>]*>(.*?)</td>', _fix_td, full_table, flags=re.DOTALL)

            # Fix <th> cells
            def _fix_th(m):
                content = m.group(1)
                content = _break_long_text(content)
                return f'<th style="word-wrap:break-word;overflow:hidden;vertical-align:top;padding:5px 6px;">{content}</th>'

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
        color: #667eea;
        font-size: 18pt;
        border-bottom: 3px solid #667eea;
        padding-bottom: 6px;
        margin-top: 18px;
    }}
    h2 {{
        color: #764ba2;
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
        table-layout: auto;
    }}
    th {{
        background-color: #667eea;
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
        color: #667eea;
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
    @st.cache_data(show_spinner=False)
    def generate_pdf(html_content):
        pdf_buffer = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html_content), dest=pdf_buffer)
        return pdf_buffer.getvalue()

    pdf_bytes = generate_pdf(pdf_html)

    # Export buttons
    col_export1, col_export2, col_export3 = st.columns(3)
    with col_export1:
        st.download_button(
            label="📥 Download (PDF)",
            data=pdf_bytes,
            file_name=f"{report_filename_base}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col_export2:
        st.download_button(
            label="📥 Download (Markdown)",
            data=report_md,
            file_name=f"{report_filename_base}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_export3:
        if st.button("🔄 Run New Analysis", use_container_width=True):
            st.session_state.pop("report", None)
            st.session_state.pop("mode", None)
            st.rerun()

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption(
    "🔒 **Read-Only Mode** — This tool only reads data from connected platforms. "
    "No modifications are made. Gemini AI is used for analysis only."
)
