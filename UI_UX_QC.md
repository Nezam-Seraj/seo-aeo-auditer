# SEO/AEO Analyzer — UI/UX Quality Check

Run this checklist after **every code update** to catch visual and interaction issues
before they reach the user. Open the app at `http://localhost:8501` in a browser.

---

## 1. Landing Page (No Mode Selected)

- [ ] **Header gradient** renders ("🔬 SEO/AEO Analyzer") — not plain text
- [ ] **Subtitle** is visible and correctly colored (#888 grey)
- [ ] **Mode buttons** — both appear as **secondary** (grey/outline), neither highlighted
- [ ] **Info prompt** — "👆 Select an analysis mode to get started." is visible
- [ ] **Comparison table** — renders with purple gradient header, 4 rows, 3 columns
- [ ] **Sidebar** opens and shows:
  - API key status indicators (green ✅ or input fields)
  - "🔄 Refresh Connections" button
  - "🔒 Read-Only Mode" caption
- [ ] **Footer** — "🔒 Read-Only Mode" caption at bottom of main area
- [ ] **No error banners** (red/orange/yellow) visible on load

---

## 2. Mode Selection & Button Highlighting

- [ ] Click **"👤 Client Analysis"** →
  - Client button turns **primary** (colored)
  - Prospect button stays **secondary** (grey)
  - Blue banner shows "Client Mode"
- [ ] Click **"🔍 Prospect / Competitor Analysis"** →
  - Prospect button turns **primary** (colored)
  - Client button stays **secondary** (grey)
  - Blue banner shows "Prospect/Competitor Mode"
- [ ] Switching modes **clears any previous report** from the page
- [ ] Switching modes does **not** produce any error

---

## 3. Client Mode UI

- [ ] **Blue info banner** displays with data source tags: GSC, Bing, Site Crawl
- [ ] **Authentication** status shows (✅ or ❌)
- [ ] **GSC Property dropdown** populates (or shows "No properties found" warning)
- [ ] **Bing Site dropdown** populates (or shows "(Skip Bing)" default)
- [ ] **"⚙️ Analysis Options"** expander opens/closes without error
  - Checkbox "Also crawl the site for technical SEO data" is present
  - Slider "Max pages to crawl" appears when checkbox is on
- [ ] **"🚀 Run Full Analysis"** button is full-width, primary styled
- [ ] Clicking **Run** without a Gemini key shows an error message (not a crash)

---

## 4. Prospect Mode UI

- [ ] **Blue info banner** displays with "Public Crawl" tag
- [ ] **URL input** shows placeholder "example.com"
- [ ] **"⚙️ Crawl Options"** expander opens/closes without error
  - Slider "Max pages to crawl" is present (range 10–100)
- [ ] **"🚀 Analyze Site"** button is full-width, primary styled
- [ ] Clicking **Analyze** with empty URL shows an error (not a crash)
- [ ] Clicking **Analyze** without a Gemini key shows an error (not a crash)

---

## 5. Report Display — Tables

> **This is the #1 source of UI bugs.** Gemini generates markdown tables that Streamlit
> sometimes fails to render. Always verify tables after every report.

- [ ] **ALL tables render as actual tables** — not raw pipe characters (`|`) or dashed lines (`---`)
- [ ] **No table has empty/blank rows** filling the page
- [ ] **Tables with 6+ columns** are horizontally scrollable, not squished
- [ ] **Table headers** have purple gradient backgrounds and white text
- [ ] **Alternating row colors** are visible (subtle purple tint on even rows)
- [ ] **Long URLs in cells** wrap properly — no horizontal page overflow
- [ ] **No table exceeds 50 data rows** (truncation message should appear if capped)

### 🔧 If Tables Are Broken — Auto-Fix Checklist

1. **Click "🔄 Run New Analysis"** — stale cached reports often cause this
2. If still broken after re-run, check `_sanitize_report_tables()` in `app.py`:
   - Is it stripping empty rows? (look for `empty_row_streak`)
   - Is it normalizing column counts? (look for `col_count`)
   - Is it capping oversized tables? (look for `> 52`)
3. If the table markdown itself is malformed (view report_md in debugger):
   - Missing separator row after header → Streamlit renders as plain text
   - Fix: ensure `| --- | --- | --- |` row exists after every header row
4. **CSS override** — if tables render but look awful, check `app.py` CSS section:
   - `.stMarkdown table` must have `table-layout: auto` (for display)
   - `min-width: 80px` on `td` prevents crushed columns

---

## 6. Report Display — Hans' Section & Content

- [ ] **"🤝 Hans' Section"** heading exists near the bottom of the report
- [ ] Contains **"The Headline"** — 1-2 sentence key finding
- [ ] Contains **"Why This Matters"** — business impact in plain language
- [ ] Contains **"The Bottom Line"** — pitch-ready summary
- [ ] Hans' Section uses **zero technical jargon** (no "crawl budget", "canonical", etc.)

### 🔧 If Hans' Section Is Missing

1. **Was the report cached from before the prompt update?** → Click "🔄 Run New Analysis"
2. Check `prompts.py` — search for `Hans' Section` in both `build_client_analysis_prompt`
   and `build_prospect_analysis_prompt`. It should be the LAST content section.
3. If Gemini is cutting it off, the report may be too long → reduce `[:50]` page limit
   in `format_crawl_context()` or add `max_output_tokens` to the Gemini call.

---

## 7. Export Buttons & Client Report

- [ ] **Row 1** shows two download buttons side by side:
  - "📥 Download Report (PDF)"
  - "📥 Download Report (Markdown)"
- [ ] **Row 2** shows two action buttons side by side:
  - "📤 Generate Client Report"
  - "🔄 Run New Analysis"
- [ ] **All buttons** are full-width within their column
- [ ] **No buttons stack vertically** in the same row (except at very narrow widths)
- [ ] **"📤 Generate Client Report"** shows spinner then renders the client report below
- [ ] **Client report** has its own download buttons (PDF + Markdown)
- [ ] **"🔄 Run New Analysis"** clears report, client report, and mode

### 🔧 If Buttons Stack Vertically

- Buttons should be in `st.columns(2)` — not `st.columns(4)` (too cramped)
- Check `app.py` for `col_dl1, col_dl2` and `col_act1, col_act2`

---

## 8. PDF Export Quality

- [ ] Downloaded PDF opens without errors
- [ ] **Landscape orientation** for internal report PDF
- [ ] **Portrait orientation** for client-facing report PDF
- [ ] **Tables** don't overflow the page margins
- [ ] **Long URLs** wrap (no horizontal overflow)
- [ ] **Footer** text appears: "Generated by SEO/AEO Analyzer" (internal) / "Prepared by Hans Digital" (client)
- [ ] If PDF fails, **warning shown** (not crash) with Markdown fallback

---

## 9. Error Handling & Edge Cases

- [ ] **Missing credentials.json** → shows clear error + hint, no crash
- [ ] **Expired OAuth token** → re-authenticates or shows actionable error
- [ ] **Network timeout** during crawl → shows warning, not crash
- [ ] **Empty crawl results** → shows "No data collected" message
- [ ] **Gemini API error** → shows "Analysis failed" with message, not traceback
- [ ] **Bing API error** → shows warning, continues without Bing data
- [ ] **Client report generation error** → shows error message, not crash

---

## 10. Responsiveness & Sidebar

- [ ] At **narrow width** (~600px): buttons stack per row, text remains legible
- [ ] At **wide width** (1400px+): layout uses space well, no stretched elements
- [ ] **Table containers** scroll horizontally when content exceeds width
- [ ] No **horizontal page scroll** at any width
- [ ] **Sidebar** API key indicators match `.env` state
- [ ] **"🔄 Refresh Connections"** clears cached data and triggers rerun

---

## Quick Post-Update Check (2 minutes)

1. **Load the app** — no errors on startup
2. **Click each mode button** — correct button highlights, correct content loads
3. **Check sidebar** — API status indicators are correct
4. **Expand an options section** — no crash
5. **If a report exists in session** — check:
   - Tables render as actual tables (not raw markdown)
   - Hans' Section is present at the bottom
   - All 4 export/action buttons are visible in 2 rows
   - "Generate Client Report" button works

✅ All checks pass → **UI is clean, ship it**
⚠️ Any failure → **Fix before pushing** (see 🔧 sections above for auto-fix steps)
