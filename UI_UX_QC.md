# SEO/AEO Analyzer — Final Boss QC Protocol

> **AGENT INSTRUCTIONS**: You are the QA gatekeeper. Run this protocol after every code update
> before the app ships. Launch the app (`streamlit run app.py`), open `http://localhost:8501`
> in your browser tools, and execute every check below **sequentially**.
>
> **REMEDIATION MANDATE**: If any check fails, **do not stop**. Read the 🔧 FIX section for
> that step, apply the fix in the codebase, restart the server, and re-run the failed check
> until it passes. Only move on when the check is green.
>
> **HANDOFF STANDARD**: When all checks pass, the app can be handed to anyone — a client,
> a team member, a stranger — and it will not break in their hands.

---

## 0. Pre-Flight — Environment & Startup

- [ ] `.env` exists in project root and contains `GEMINI_API_KEY=...` and `BING_API_KEY=...`
- [ ] `.env.example` exists (so a new user knows what keys are needed)
- [ ] `credentials.json` exists in project root (Google OAuth file)
- [ ] `token.json` exists (cached OAuth token)
- [ ] Run `streamlit run app.py` — app starts **without any Python traceback in the terminal**
- [ ] Browser loads `http://localhost:8501` — page renders within 5 seconds, no white screen

### 🔧 FIX: Startup Failures
1. **Missing `.env`**: Copy `.env.example` → `.env` and fill in real keys.
2. **Import errors in terminal**: Run `pip install -r requirements.txt` inside `.venv`.
3. **`credentials.json` not found**: Download from Google Cloud Console → OAuth 2.0 Client IDs.
4. **White screen / connection refused**: Check terminal for port conflict. Kill other Streamlit instances.

---

## 1. Landing Page — Zero-State Integrity

When no mode is selected, the landing page must be clean, professional, and error-free.

### Visual Checks
- [ ] **Header** — "🔬 SEO/AEO Analyzer" renders with a **purple gradient text fill** (not plain black text). Inspect: look for the `.main-header` class with `linear-gradient(135deg, #667eea, #764ba2)` and `-webkit-background-clip: text`.
- [ ] **Subtitle** — visible below header, grey text (#888), reads: "Comprehensive site analysis powered by Gemini AI — using data from Google Search Console, GA4, Google Business Profile, and Bing Webmaster Tools"
- [ ] **Mode buttons** — both "👤 Client Analysis" and "🔍 Prospect / Competitor Analysis" appear **side by side** in a 2-column layout. **Both are secondary style** (grey/outline) — neither is highlighted as primary.
- [ ] **Info prompt** — "👆 Select an analysis mode to get started." is visible between the buttons and the table.
- [ ] **Comparison table** — renders as an actual HTML `<table>` with purple gradient headers and 4 data rows (Data Sources, Best For, Depth, Requires Auth). Columns: blank, Client Analysis, Prospect/Competitor.
- [ ] **Footer** — "🔒 Read-Only Mode" caption visible at the bottom of the main content area.

### Sidebar Checks
- [ ] Sidebar header shows "⚙️ Settings"
- [ ] **Gemini API key** — shows green "✅ Gemini API key loaded from .env" (if key exists in `.env`) **or** shows a password input field (if key is missing)
- [ ] **Bing API key** — shows green "✅ Bing API key loaded from .env" (if key exists) **or** shows a password input field
- [ ] **"🔄 Refresh Connections"** button is present and full-width
- [ ] **"🔒 Read-Only Mode"** caption is present in the sidebar

### Error Scan
- [ ] **CRITICAL**: Scan the entire page for red/orange/yellow error banners, exception tracebacks, or `st.exception` elements. **ASSERT NONE EXIST.**

### 🔧 FIX: Landing Page Issues
- **Buttons show as primary when no mode selected**: Open `app.py` line ~211-224. Verify `type="primary" if st.session_state.get("mode") == "client" else "secondary"` — the conditional must check `st.session_state.get("mode")`, not a hardcoded value.
- **Gradient not rendering**: Check that the CSS block (line ~29-146) includes `.main-header` with `-webkit-background-clip: text` and `-webkit-text-fill-color: transparent`.
- **Table renders as raw markdown pipes**: Ensure the markdown table in the `if not mode:` block (line ~240-247) has proper formatting — header row, separator row (`|---|---|---|`), data rows. Each must start and end with `|`.
- **API key status wrong**: Check `config.py` — verify `load_dotenv()` is called before `os.environ.get()`.

---

## 2. Mode Selection — State Management

### Client Mode Activation
- [ ] Click **"👤 Client Analysis"**
- [ ] **ASSERT**: Client button switches to **primary** (colored/filled) style
- [ ] **ASSERT**: Prospect button remains **secondary** (grey/outline) style
- [ ] **ASSERT**: Blue banner appears with text containing "Client Mode" and data source tags (GSC, Bing, Site Crawl)
- [ ] **ASSERT**: The comparison table and "Select an analysis mode" prompt **disappear**

### Prospect Mode Activation
- [ ] Click **"🔍 Prospect / Competitor Analysis"**
- [ ] **ASSERT**: Prospect button switches to **primary** style
- [ ] **ASSERT**: Client button reverts to **secondary** style
- [ ] **ASSERT**: Blue banner appears with text containing "Prospect/Competitor Mode" and "Public Crawl" tag
- [ ] **ASSERT**: All Client Mode UI elements (GSC dropdown, auth status, etc.) are **gone from the DOM**

### State Bleed Check
- [ ] Switch from Client → Prospect → Client rapidly (3 times)
- [ ] **ASSERT**: No error banners appear at any point during switching
- [ ] **ASSERT**: No stale data from a previous mode appears in the current mode
- [ ] **ASSERT**: `st.session_state["report"]`, `st.session_state["client_report"]`, and `st.session_state["report_filename"]` are all cleared when switching modes (no ghost reports)

### Cross-Mode Report Bleed Test (CRITICAL)
- [ ] Run a **full client analysis** → generate the client report → verify it displays
- [ ] Switch to **Prospect Mode** → run a new analysis on a different site
- [ ] **ASSERT**: Only the new prospect report appears — the old client analysis and client-facing report are **completely gone**
- [ ] **ASSERT**: Download buttons produce files for the prospect site, not the previous client site

### 🔧 FIX: State Issues
- **Both buttons appear primary**: Check `app.py` line ~226-234. The `st.session_state.pop("report", None)` must fire on mode switch, and `st.rerun()` must be called after.
- **Stale report persists after mode switch**: Verify that both `client_selected` and `prospect_selected` blocks call `st.session_state.pop()` on ALL three keys: `"report"`, `"client_report"`, and `"report_filename"`.
- **Error on rapid switching**: This usually means a variable from one mode leaks into the other. Check that all mode-specific variables are guarded by `if mode == "client":` / `elif mode == "prospect":`.

---

## 3. Client Mode — Full UI Validation

Precondition: Click "👤 Client Analysis" to enter Client Mode.

### Authentication & Dropdowns
- [ ] **Auth status** — "✅ Google authenticated!" success banner appears (if `credentials.json` and `token.json` are valid)
- [ ] **GSC Property dropdown** — populated with at least one property URL, **or** shows "No Search Console properties found." warning
- [ ] **Bing Site dropdown** — populated with site list and "(Skip Bing)" as first option, **or** shows a text input fallback, **or** shows "ℹ️ Add Bing API key in sidebar" caption

### Analysis Options
- [ ] **"⚙️ Analysis Options"** expander renders and can be opened/closed without error
- [ ] Inside expander: **checkbox** "Also crawl the site for technical SEO data" is present (default: checked)
- [ ] Inside expander: **slider** "Max pages to crawl" appears (range 10–100, step 10, default 30) — only visible when checkbox is checked
- [ ] Uncheck the crawl checkbox → slider **disappears**. Re-check → slider **reappears**. No error.

### Run Button
- [ ] **"🚀 Run Full Analysis"** button is visible, **primary** styled, **full-width**
- [ ] Click Run **without a Gemini key** in `.env` or sidebar → **ASSERT**: red error "❌ Please provide a Gemini API key in the sidebar." appears. **ASSERT**: app does NOT crash (no Python traceback).

### 🔧 FIX: Client Mode Issues
- **Auth fails**: Check `credentials.json` is valid. Delete `token.json` and re-authenticate. Verify `config.py` SCOPES list matches what the OAuth consent screen allows.
- **GSC dropdown empty when properties exist**: Check `collectors/gsc.py` → `list_properties()`. Verify the API call uses the correct credentials and scope `webmasters.readonly`.
- **Slider doesn't hide/show**: Verify `app.py` line ~345 has `if include_crawl` guarding the slider.

---

## 4. Prospect Mode — Full UI Validation

Precondition: Click "🔍 Prospect / Competitor Analysis" to enter Prospect Mode.

### Form Elements
- [ ] **Blue info banner** — displays with "Prospect/Competitor Mode" text and "Public Crawl" tag
- [ ] **URL input** — text field with placeholder "example.com"
- [ ] **"⚙️ Crawl Options"** expander renders and opens/closes without error
- [ ] Inside expander: **slider** "Max pages to crawl" (range 10–100, step 10, default 30)

### Validation
- [ ] **"🚀 Analyze Site"** button is visible, **primary** styled, **full-width**
- [ ] Click Analyze with **empty URL** → **ASSERT**: red error "❌ Please enter a URL." appears. **ASSERT**: no crash.
- [ ] Click Analyze with a URL but **no Gemini key** → **ASSERT**: red error about missing API key. **ASSERT**: no crash.

### 🔧 FIX: Prospect Mode Issues
- **Crash on empty URL**: Check `app.py` line ~457-459. The `if not target_url:` guard must come before any crawl logic. Verify `st.stop()` is called after the error.
- **Crash on missing key**: Check `app.py` line ~460-462. Same pattern — guard + `st.stop()`.

---

## 5. Report Display — Table Rendering (THE #1 BUG SOURCE)

> ⚠️ **This is the most volatile part of the app.** Gemini generates markdown tables that
> Streamlit sometimes fails to render. Every single report must be checked here.

Precondition: Trigger a successful analysis (either mode) so a report is displayed.

### Table Integrity
- [ ] **ALL tables** in the report render as actual HTML `<table>` elements — not raw pipe characters (`|`) or dashed lines (`---`) shown as plain text
- [ ] **No table has excessive empty/blank rows** filling the page
- [ ] **Column counts are consistent** — every row in a table has the same number of columns as the header
- [ ] **Tables with 6+ columns** are horizontally scrollable within their container, not squished to illegibility

### Table Styling
- [ ] **Table headers** have purple gradient backgrounds (`linear-gradient(135deg, #667eea, #764ba2)`) and white text
- [ ] **Alternating row colors** — even rows have a subtle purple tint (`rgba(102, 126, 234, 0.04)`)
- [ ] **Row hover** — hovering over a row shows a slightly deeper tint (`rgba(102, 126, 234, 0.08)`)
- [ ] **Long URLs in cells** wrap properly — no single cell causes horizontal page overflow

### Table Size Limits
- [ ] **No table exceeds 50 data rows** — if the source data is larger, a truncation message appears: "*... table truncated for readability (showing first 50 rows) ...*"

### 🔧 FIX: Broken Tables — Step-by-Step
1. **Try "🔄 Run New Analysis" first** — stale cached reports are the most common cause.
2. **If still broken**, inspect `_sanitize_report_tables()` in `app.py` (line ~556-639):
   - Is it stripping empty rows? Look for `empty_row_streak` logic.
   - Is it normalizing column counts? Look for `col_count` padding/trimming.
   - Is it capping oversized tables? Look for `> 52` (header + separator + 50 rows).
3. **If raw markdown pipes (`|`) are visible as text**: The table is missing the separator row after the header. The regex in `_sanitize_report_tables()` should ensure a `| --- | --- |` row exists after every header row. If Gemini is generating tables without separators, add post-processing in the `_flush_table()` inner function to inject one.
4. **If tables render but look squished**: Check `app.py` CSS (line ~106-144):
   - `.stMarkdown table` must have `table-layout: fixed` (for PDF) but the display container needs `overflow-x: auto` for scrollability.
   - `td` must have `word-break: break-all` and `max-width: 250px`.

---

## 6. Report Content — Hans' Section

Precondition: A report is displayed after a successful analysis.

### Presence Check
- [ ] **"🤝 Hans' Section"** heading exists near the **bottom** of the report (search for the exact string)

### Structure Check
- [ ] Contains a sub-heading or bolded label: **"The Headline"** — 1-2 sentence key finding
- [ ] Contains **"Why This Matters"** — business impact in plain language
- [ ] Contains **"The Bottom Line"** — pitch-ready summary

### Jargon Check
- [ ] Parse all text within the Hans' Section. Scan against this blacklist: `["crawl budget", "canonical", "hreflang", "status code", "robots.txt", "noindex", "schema markup", "sitemap", "301 redirect", "alt tags", "meta description", "backlink", "domain authority"]`
- [ ] **ASSERT NO MATCHES.** Hans' Section must be 100% jargon-free — written for a business owner, not a developer.

### 🔧 FIX: Hans' Section Issues
1. **Missing entirely**: Click "🔄 Run New Analysis" — it may be a cached report from before the prompt was updated.
2. **Still missing after re-run**: Open `agent/prompts.py`, search for `Hans' Section`. Verify it appears in **both** `build_client_analysis_prompt()` (line ~235) and `build_prospect_analysis_prompt()` (line ~444). It must be the **last content section** in the prompt.
3. **Cut off mid-sentence**: Gemini hit its output token limit. In `agent/orchestrator.py`, add `generation_config={"max_output_tokens": 8192}` to the `generate_content()` call, or reduce the input context size by lowering the page limit in `format_crawl_context()`.
4. **Contains jargon**: Update the Hans' Section instructions in `agent/prompts.py` to explicitly list the banned terms and instruct: "If you catch yourself using any of these words, rephrase in plain business language."

---

## 7. Export Buttons — Layout & Functionality

Precondition: A report is displayed.

### Button Layout
- [ ] **Row 1** (Downloads): Two buttons **side by side** in a 2-column layout:
  - "📥 Download Report (PDF)"
  - "📥 Download Report (Markdown)"
- [ ] **Row 2** (Actions): Two buttons **side by side** in a 2-column layout:
  - "📤 Generate Client Report"
  - "🔄 Run New Analysis"
- [ ] **All four buttons** are full-width within their respective column
- [ ] **No buttons stack vertically** within the same row (except at extreme narrow widths < 500px)

### Download Tests
- [ ] **Markdown download**: Click "📥 Download Report (Markdown)" → file downloads. **ASSERT**: file extension is `.md`, file size > 0 bytes.
- [ ] **PDF download** (if available): Click "📥 Download Report (PDF)" → file downloads. **ASSERT**: file extension is `.pdf`, file size > 0 bytes, file opens without errors.
- [ ] **PDF fallback**: If PDF generation fails, **ASSERT**: a warning "⚠️ PDF generation failed — download as Markdown instead." appears — **not** a crash.

### Client Report Generation
- [ ] Click **"📤 Generate Client Report"**
- [ ] **ASSERT**: A spinner appears ("✨ Generating client-facing report...")
- [ ] **ASSERT**: After completion, a new section "📤 Client-Facing Report" appears below the internal report
- [ ] **ASSERT**: The client report has its **own** download buttons — "📥 Download Client Report (PDF)" and "📥 Download Client Report (Markdown)" — also in a 2-column layout
- [ ] Click "📤 Generate Client Report" **without a Gemini key** → **ASSERT**: error message appears, no crash

### Run New Analysis
- [ ] Click **"🔄 Run New Analysis"**
- [ ] **ASSERT**: Report disappears, Client Report disappears, mode resets to none, landing page is shown

### 🔧 FIX: Export Issues
- **Buttons stack vertically**: Open `app.py`, find `col_dl1, col_dl2 = st.columns(2)` (line ~906) and `col_act1, col_act2 = st.columns(2)` (line ~928). Buttons must be inside `with col_dl1:` / `with col_dl2:` blocks, not raw `st.button()` calls outside columns.
- **PDF crash**: Check `import io, re, markdown` and `from xhtml2pdf import pisa` (line ~550-553). Verify `xhtml2pdf` is installed. Check that `_strip_emojis_for_pdf()` is stripping all emoji before passing HTML to xhtml2pdf.
- **Client report generation crash**: Check `agent/orchestrator.py` → `generate_client_facing_report()`. Verify the Gemini API call has proper error handling.

---

## 8. PDF Export Quality — Deep Validation

Precondition: Download both the internal report PDF and the client report PDF.

### Internal Report PDF
- [ ] PDF opens without errors in any PDF reader
- [ ] **Orientation**: **Landscape** (width > height). Verify: `@page { size: letter landscape; }` at `app.py` line ~791.
- [ ] **Tables** don't overflow page margins — columns are proportionally sized
- [ ] **Long URLs** wrap within cells (zero-width space insertion working)
- [ ] **Footer** text at bottom: "Generated by SEO/AEO Analyzer — Data sourced from Google Search Console, GA4, GBP, and Bing Webmaster Tools"
- [ ] **No emoji characters** visible in the PDF (they should be replaced with text equivalents like `[OK]`, `[!]`, `[X]`)

### Client Report PDF
- [ ] PDF opens without errors
- [ ] **Orientation**: **Portrait** (height > width). Verify: `@page { size: letter portrait; }` at `app.py` line ~980-981.
- [ ] **Tables** don't overflow margins
- [ ] **Footer** text: "Prepared by Hans Digital - Confidential"
- [ ] **No Hans' Section** appears in the client report (it's internal-only)
- [ ] **No confidence tags** like `[DATA]`, `[INFERRED]`, `[ESTIMATED]` appear (internal-only)
- [ ] **No raw technical jargon** — phrased for business owners

### 🔧 FIX: PDF Issues
- **PDF is blank or tiny (< 100 bytes)**: Check `app.py` line ~891-903. Verify `pisa.CreatePDF()` isn't silently failing. Print `pisa_status.err` and `pisa_status.log` to terminal for debugging.
- **Emoji causing PDF failure**: Open `_strip_emojis_for_pdf()` in `app.py` (line ~524-549). Add the failing emoji to the `emoji_map` dict. The catch-all regex should handle unmapped emoji, but some edge cases slip through.
- **Tables overflow in PDF**: Check `_fix_tables_for_pdf()` (line ~665-782). Verify `colgroup` width percentages are being calculated and injected. Verify `word-wrap: break-word` is on every `<td>`.
- **Hans' Section in client report**: Check `agent/orchestrator.py` line ~147. The prompt must contain: "Do NOT include the Hans' Section — that was for internal use."

---

## 9. Error Handling & Edge Cases — Stress Tests

These checks verify the app **fails gracefully** under adverse conditions. The golden rule:
**The user should NEVER see a Python traceback. Every failure must show a human-readable error message.**

### Authentication Failures
- [ ] **Missing `credentials.json`**: Rename `credentials.json` → `credentials.json.bak`, enter Client Mode. **ASSERT**: clear error "❌ credentials.json not found..." with hint to download from Google Cloud Console. **ASSERT**: no crash. **Restore the file after.**
- [ ] **Expired OAuth token**: If `token.json` contains an expired token, the app should either silently refresh it or show an actionable re-auth prompt — not a traceback.

### API Failures
- [ ] **Gemini API error** (rate limit, quota, bad key): The app shows "❌ Analysis failed: [message]" — not a raw traceback.
- [ ] **Bing API error** (bad key, network): The app shows "⚠️ Bing collection failed: [message]" and **continues** the analysis without Bing data — does not crash.
- [ ] **GSC API error**: Shows "⚠️ GSC collection failed: [message]" — continues if other data sources available.

### Crawl Failures
- [ ] **Invalid URL** (e.g., "not-a-url"): The crawl fails gracefully with an error message, not a crash.
- [ ] **Unreachable site** (e.g., site is down): Shows warning about failed crawl — not a Python traceback.
- [ ] **Empty crawl results** (site blocks bots): Show a "No data collected" message.

### Network Issues
- [ ] **Network timeout during crawl**: Warning message displayed, not a crash. Check `config.py` → `CRAWL_TIMEOUT = 10` is a reasonable value.

### 🔧 FIX: Error Handling Gaps
- **Any raw traceback visible to user**: Locate the offending function call. Wrap it in a `try/except` block. Use `st.error()` for fatal errors, `st.warning()` for non-fatal. Always call `st.stop()` after fatal errors to prevent cascading failures.
- **App hangs indefinitely**: Add timeout parameters to all HTTP/API calls. Crawl timeout is in `config.py` (`CRAWL_TIMEOUT`). Gemini API should use `timeout` parameter if available.

---

## 10. Responsiveness & Layout Integrity

### Width Tests
- [ ] **Narrow width (~600px)**: Buttons may stack per row (acceptable), text remains legible, no horizontal page scroll
- [ ] **Normal width (~1200px)**: 2-column button layout works, tables fit, sidebar is usable
- [ ] **Wide width (1400px+)**: Layout uses space well, no stretched/distorted elements
- [ ] **At ALL widths**: No horizontal page scrollbar on the main page body (table containers may scroll internally — that's fine)

### Table Containers
- [ ] Tables wider than their container scroll **horizontally within their container** — the page itself does not scroll
- [ ] Verify CSS: `.stMarkdown div[data-testid="stMarkdownContainer"]` has `overflow-x: auto`

### Sidebar
- [ ] API key indicators match `.env` state at all widths
- [ ] "🔄 Refresh Connections" clears cached data and triggers a full rerun (verify: sidebar indicators re-render)

---

## 11. Data Integrity Cross-Check

> This section validates that the app doesn't corrupt, lose, or hallucinate data between
> collection and display. Cross-reference with `DATA_VALIDATION.md` for the full checklist.

### Session State Integrity
- [ ] After a successful analysis, `st.session_state["report"]` contains a non-empty markdown string
- [ ] `st.session_state["report_filename"]` is a valid filename string (no special characters that would break download)
- [ ] After clicking "🔄 Run New Analysis", both `report` and `client_report` are **fully purged** from session state

### Report Content Sanity
- [ ] The report contains an `# 🔍 SEO/AEO Site Analysis Report` header (from `agent/report.py`)
- [ ] The report contains **Site**, **Mode**, **Generated**, and **Data Window** metadata fields
- [ ] The analysis content is **not empty** — there is substantial text beyond just the header

---

## Quick Post-Update Smoke Test (2 minutes)

> Use this abbreviated checklist when you've made a small code change and need a fast sanity check.
> For major changes, run the full protocol above.

1. **Load the app** — no errors on startup, no tracebacks in terminal
2. **Check sidebar** — API status indicators show correct state (green ✅ if keys present)
3. **Click each mode button** — correct button highlights, correct banner appears, no errors
4. **Expand an options section** — opens/closes without crash
5. **If a report exists in session** — verify:
   - Tables render as actual tables (not raw markdown)
   - Hans' Section is present at the bottom
   - All 4 export/action buttons visible in 2 rows of 2
   - "📤 Generate Client Report" doesn't crash
6. **Switch modes** — previous report clears, no stale data

---

## Appendix: File Reference Map

Quick reference for where each feature lives in the codebase:

| Feature | File | Key Lines / Functions |
|---|---|---|
| Page config & CSS | `app.py` | Lines 20-146 |
| Header & subtitle | `app.py` | Lines 151-156 |
| Sidebar (API keys, settings) | `app.py` | Lines 161-201 |
| Mode selector buttons | `app.py` | Lines 208-248 |
| Client Mode UI | `app.py` | Lines 253-431 |
| Prospect Mode UI | `app.py` | Lines 436-517 |
| Table sanitizer | `app.py` | `_sanitize_report_tables()` — line 556 |
| Emoji stripper (PDF) | `app.py` | `_strip_emojis_for_pdf()` — line 524 |
| PDF table fixer | `app.py` | `_fix_tables_for_pdf()` — line 665 |
| Report display & export | `app.py` | Lines 645-1100 |
| Internal report PDF template | `app.py` | Lines 786-888 (landscape) |
| Client report PDF template | `app.py` | Lines 975-1062 (portrait) |
| Google OAuth | `auth.py` | `get_credentials()` |
| API keys & defaults | `config.py` | `GEMINI_API_KEY`, `BING_API_KEY`, `GEMINI_MODEL` |
| Gemini analysis prompts | `agent/prompts.py` | `build_client_analysis_prompt()`, `build_prospect_analysis_prompt()` |
| Hans' Section prompt | `agent/prompts.py` | Lines ~235, ~444 |
| Gemini orchestration | `agent/orchestrator.py` | `run_client_analysis()`, `run_prospect_analysis()`, `generate_client_facing_report()` |
| Report header/filename | `agent/report.py` | `format_report_header()`, `get_report_filename()` |
| GSC collector | `collectors/gsc.py` | `list_properties()`, `collect_all()` |
| Bing collector | `collectors/bing.py` | `get_sites()`, `collect_all()` |
| Crawler | `collectors/crawler.py` | `crawl_site()` |

---

✅ **All checks pass** → App is battle-tested. Ship it with confidence.
⚠️ **Any failure** → Fix it using the 🔧 sections above. Do not ship until every check is green.
