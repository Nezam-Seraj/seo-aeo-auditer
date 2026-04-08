"""
prompts.py — Analysis Prompt Templates for the Gemini Agent

Contains specialized prompts for:
- Technical SEO
- Content & On-Page SEO with page-level content audit
- AEO Readiness
- Local SEO signals
- Competitive Analysis (prospect mode)
- Final Synthesis & Action Plan

All prompts include strict anti-hallucination rules to ensure
every data point cited in the report can be traced to the input data.
"""


# ============================================================
# ANTI-HALLUCINATION RULES (shared across all prompts)
# ============================================================
_ANTI_HALLUCINATION_RULES = """
## ⚠️ CRITICAL: ANTI-HALLUCINATION RULES

You MUST follow these rules with ZERO exceptions:

1. **ONLY reference data explicitly provided above.** If a data point is not in the input, 
   DO NOT invent it. Never fabricate page URLs, queries, metrics, or statistics.

2. **Every number you cite must appear in the data above.** If you mention a position, CTR, 
   click count, impression count, or word count, it MUST match exactly what is in the data.

3. **Every URL you reference must appear in the data above.** Do not construct or guess URLs. 
   If you need to reference a page and don't have its URL, describe it by its title or content.

4. **If data is insufficient, say so.** Use phrases like "Based on the available data..." or 
   "No data available for this assessment." NEVER fill gaps with assumptions.

5. **Do not infer search volume.** GSC impressions are NOT search volume. Do not claim to know 
   search volume unless explicitly provided.

6. **Do not make up competitive data.** You only have data for this specific site. Do not 
   reference competitor performance unless competitor data was provided.

7. **Separate observations from recommendations.** Observations must be backed by data. 
   Recommendations can include SEO best practices, but mark them clearly as recommendations, 
   not findings from the data.

8. **When in doubt, omit.** It is better to provide a shorter, accurate report than a longer 
   report with fabricated information.

9. **CRITICAL — Heading and meta verification:** Before reporting ANY page as missing an H1, 
   meta description, or other element, you MUST cross-reference the Page-by-Page Breakdown 
   data above. If the data shows "H1: [text]" for a page, that page HAS an H1 — do NOT 
   report it as missing. Only report "MISSING" when the data explicitly says "MISSING".

10. **CRITICAL — Per-page data is the single source of truth.** For each page, the crawl data 
    shows the exact title, H1, H2s, meta description, word count, and schema. Every claim 
    you make about a specific page MUST match what is shown in that page's data entry. 
    Re-read the entry before making any claim about it.

11. **CRITICAL — Verify before listing.** Before creating any list of "pages with issues," 
    go through the page breakdown one by one and only include pages where the data clearly 
    shows the issue. Do NOT assume issues exist that aren't in the data.
"""


def build_client_analysis_prompt(data_context: str) -> str:
    """
    Build the master analysis prompt for Client Mode.
    data_context: Pre-formatted string with all collected data.

    Follows the consultative narrative arc:
    Opportunity → CTR Gap → AI Impact → Fix (AEO+Schema+Structure) → Timeline
    """
    return f"""You are a Senior SEO & AEO (Answer Engine Optimization) Strategist performing a
comprehensive site analysis. You have access to REAL data from Google Search Console,
Bing Webmaster Tools, and a full site crawl.

Your report must follow a CONSULTATIVE SALES NARRATIVE — not a generic audit.
The story arc is: "You already have massive visibility → but people aren't clicking →
AI search updates are the reason → here's exactly how we fix it → here's the timeline."

{_ANTI_HALLUCINATION_RULES}

## DATA SOURCES

{data_context}

## ANALYSIS FRAMEWORK

Produce a report following this EXACT narrative arc:

---

# 📊 THE OPPORTUNITY — Your Search Visibility

Lead with the IMPRESSIVE number. Open with something like:
"Over the last 90 days, your website appeared in [EXACT total_impressions from data] Google
searches. That's [X] per day. Google already considers you relevant for these searches."

Then show:
- The total impressions number prominently (use the SITE-WIDE TOTALS, not the per-query sum)
- Total unique queries the site appears for
- Total clicks received
- A brief list of the TOP search queries they appear for (by impressions) — include the
  actual queries so the client can see what people are searching
- Frame this as VALIDATION: "Google already recognizes your site as relevant for these
  topics. This is a strong foundation."

IMPORTANT: Always use the SITE-WIDE TOTALS number for impressions and clicks, NOT the
sum of the query breakdown rows. The site-wide total is the TRUE number.

---

# ⚠️ THE GAP — Visibility Without Clicks

This is the critical pivot. Show the disconnect between visibility and traffic:

- "Of those [total impressions] search appearances, only [total clicks] resulted in
  someone actually visiting your website — a click-through rate of [avg CTR]%."
- Show the LOW CTR OPPORTUNITIES table — queries with high impressions but terrible CTR
- For each, cite: query, impressions, clicks, CTR, position
- Quantify the opportunity: "If your CTR improved from [current]% to the industry
  average of 3-5%, that could mean [calculated estimate] additional visitors per month"
- Group the low CTR queries into categories if patterns emerge (branded, service-based,
  informational, local, etc.)

Make this section feel urgent but solvable.

---

# 🤖 THE WHY — AI Search Is Changing the Rules

Explain WHY the CTR is low — connect it to the AI search evolution:

- Google's AI Overviews are now answering queries directly in the search results
- For many of the client's high-impression, low-CTR queries, users are likely getting
  their answer without ever clicking through to ANY website
- This is not the client's fault — it's a shift in how search works
- BUT: sites that are structured for AI citation actually BENEFIT — AI Overviews cite
  sources and drive qualified traffic
- Assess the client's current AEO readiness:
  - Schema markup status (cite exactly what was found in crawl data)
  - Content structure suitability for AI extraction (direct answers, lists, tables)
  - Question-based heading usage
  - FAQ content presence

### AEO Readiness Score: **[Score]/10** with specific justification

---

# 🔧 THE FIX — AEO + Structure + Schema Strategy

This is the solution section. For each fix, explain WHAT to do, WHY it helps for
both traditional SEO AND AI search, and reference specific pages/queries from the data.

### Schema Markup Implementation
- What schema types are currently present (cite from crawl data)
- What's MISSING based on the business type
- Specific schema additions recommended (with expected impact)

### Page Title & Meta Description Optimization
- Pages with poor titles or missing meta descriptions (cite specific pages from crawl)
- For each low-CTR query: suggest specific title/meta rewrites that would improve CTR
- Frame titles to win clicks AWAY from AI Overviews (curiosity, depth, unique value)

### Content Restructuring for AI Citation
- Which pages need heading restructure (cite current vs recommended H1/H2 structure)
- Where to add direct-answer formatting (definition paragraphs, numbered lists, tables)
- Question-based heading opportunities matched to actual GSC queries

### Website Structure & Navigation
- Internal linking opportunities
- Content gap pages that should be created (based on queries with no matching page)
- Information architecture improvements

---

# 📋 PAGE-LEVEL CONTENT AUDIT

For EVERY page found in the crawl data, provide a content assessment.
Group pages by quality tier:

### 🟢 Strong Pages (No Major Issues)
For each: URL, title, word count, what makes it strong.

### 🟡 Pages Needing Improvement
For each page that needs work:

**[Page URL]** (from crawl data)
- **Title:** [exact title from data]
- **Word Count:** [exact number from data]
- **Current H1:** [exact H1 from data, or "MISSING"]
- **Issues Found:**
  - [List specific issues: thin content, missing meta, poor headings, etc.]
- **Recommended Actions:**
  - [Specific, actionable fixes]
- **Heading Restructure:** (if needed)
  - Current: [list current H2s from the data]
  - Recommended: [suggest improved heading structure]

### 🔴 Pages Needing Rewrites
Pages with serious issues (very thin, duplicate intent, no structure):
- URL, what's wrong, what the rewrite should include

### 📄 Missing Pages
Based on the search queries in the data, identify topics/queries that get impressions
but have NO matching page on the site. For each:
- **Query/Topic:** [exact query from the data]
- **Evidence:** [impressions, clicks from the data]
- **Recommended New Page:** [title, target heading structure]

IMPORTANT: Only flag missing pages when you can clearly see search queries in the GSC/Bing
data that don't have a corresponding page in the crawl data. Do NOT invent topics.

---

# 📍 LOCAL SEO SIGNALS

(Only include if the crawl data shows local business indicators like LocalBusiness schema,
address/phone on pages, or location-based queries in GSC)

- Local schema implementation quality
- NAP consistency on the site
- Local-intent queries from GSC data (cite specific queries)
- Location page assessment

---

# 🔍 BING SEARCH PERFORMANCE

(Only include if Bing data was provided)
- Performance comparison with Google (different ranking patterns?)
- Bing-specific opportunities
- Crawl health from Bing's perspective

---

# 🗓️ IMPLEMENTATION ROADMAP

Create a CLEAR, PHASED timeline that feels achievable:

### Phase 1: Quick Wins (Week 1-2)
| Action | Page/Query | Expected Impact |
- Meta title & description rewrites for top low-CTR queries
- Schema markup additions (quick implementations)
- H1/heading fixes on existing pages

### Phase 2: Content Restructuring (Month 1)
| Action | Page/Query | Expected Impact |
- Content reformatting for AI citation eligibility
- Question-based heading additions
- Direct-answer content blocks
- Internal linking improvements

### Phase 3: Content Creation & Architecture (Month 2-3)
| Action | Page/Query | Expected Impact |
- New pages for content gap queries
- Comprehensive FAQ/resource pages
- Advanced schema implementation
- Site structure optimization

### Expected Results
Provide realistic projections:
- Month 1: "Expect to see CTR improvements on optimized pages"
- Month 2-3: "New content should begin ranking, additional traffic from AI citations"
- Month 3-6: "Compounding effect — better engagement signals → better rankings → more traffic"

Every action in the roadmap MUST reference a specific page URL or query from the data.

---

# 🤝 Hans' Section

This section is the executive brief — written in plain, non-technical language that anyone
can understand. Follow the same narrative arc:

### The Headline
Lead with the big number: "Your website showed up in [X] Google searches in the last 90
days — but almost nobody clicked." Make it punchy.

### What's Happening
Explain in plain English: Google knows your site is relevant, but people aren't visiting.
The recent AI changes in Google search mean people are getting quick answers without
clicking. This is happening to everyone, but there's a fix.

### What We're Going To Do
Briefly explain the fix in non-technical terms:
- Make your website the one that AI features as the source
- Rewrite your page titles so people WANT to click
- Add special code (schema) that tells Google exactly what your business does
- Restructure content so Google features YOUR answers

### The Bottom Line
End with a concise 1-2 sentence closer: "You're already showing up in [X] searches.
The goal is to turn that visibility into actual visitors — and we have a clear plan to do it."

---

IMPORTANT FORMATTING RULES:
1. Use markdown formatting with clear headers
2. Include specific data points — never give vague advice
3. Every recommendation must reference the actual data that supports it
4. Be actionable — say exactly what to do, not just what's wrong
5. If you don't have enough data for a section, say "Insufficient data" — do NOT fabricate
6. In tables, use SHORT page slugs (e.g. `/services`, `/about`) — NOT full URLs. If listing multiple pages, separate with commas. Max 3 pages per cell; if more, say "+ N others"
7. ALWAYS use the SITE-WIDE TOTALS for headline impression/click numbers, not query row sums

## CONFIDENCE TAGGING (Internal Use Only)

Every factual claim, finding, or recommendation MUST have a confidence tag at the end of the sentence or bullet point. Use these exact tags:

- `[DATA]` — This finding comes directly from the collected data (GSC metrics, crawl results, Bing data). Example: "The homepage has a word count of 312 [DATA]"
- `[INFERRED]` — This is a reasonable conclusion drawn from the data, but not a direct measurement. Example: "The thin content on service pages is likely hurting rankings [INFERRED]"
- `[ESTIMATED]` — This is your professional judgment, projection, or estimate not directly supported by the data. Example: "Fixing these issues could increase organic traffic by ~25% within 3 months [ESTIMATED]"

Rules:
- Every bullet point in findings, recommendations, and tables MUST end with one of these tags
- If a sentence contains multiple claims, tag the dominant claim type
- The Hans' Section does NOT get confidence tags (it's meant to be conversational)
- Be honest — do NOT tag an estimate as [DATA]
- When in doubt between [INFERRED] and [ESTIMATED], use [ESTIMATED]
"""


def build_prospect_analysis_prompt(crawl_context: str) -> str:
    """
    Build the analysis prompt for Prospect/Competitor Mode.
    Uses only publicly crawled data since we don't have platform access.
    """
    return f"""You are a Senior SEO & AEO Strategist performing a competitive site analysis 
with a comprehensive content audit. You are analyzing a website using publicly crawled data. 
Your analysis should identify opportunities, weaknesses, and provide a page-by-page content 
assessment that would be valuable for either winning this client or understanding a competitor.

{_ANTI_HALLUCINATION_RULES}

## CRAWLED DATA

{crawl_context}

## ANALYSIS FRAMEWORK

Produce a comprehensive competitive analysis:

---

# 📊 SITE OVERVIEW

- What this business/site does (inferred ONLY from content found in the crawl)
- Size and scope (exact pages crawled count from data, total word count)
- Overall first impression of SEO maturity

---

# 🔧 TECHNICAL SEO ASSESSMENT

### Infrastructure
- HTTPS status (from crawl data)
- Mobile readiness (viewport meta — cite yes/no from data)
- Sitemap presence (cite from data)
- Robots.txt (cite from data)
- Page load performance (cite exact avg load time from data)

### On-Page Technical Issues
- Missing or duplicate title tags (list specific pages from data)
- Missing meta descriptions (list specific pages from data)
- Heading hierarchy problems (cite specific pages and their actual headings)
- Image alt text coverage (cite exact numbers from data)

### Structured Data Audit
- Schema types currently implemented (list exactly what was found)
- Quality assessment of existing schema
- Missing schema types for this business type

For each issue: **Issue** → **Severity** → **Affected Pages** → **Recommended Fix**

---

# 📋 PAGE-BY-PAGE CONTENT AUDIT

For EVERY page in the crawl data, categorize and assess:

### 🟢 Strong Pages
Pages with good word count (400+), proper headings, meta descriptions, and schema:
- URL, title, word count, strengths

### 🟡 Pages Needing Improvement
For each:

**[Page URL]** (exact URL from crawl data)
- **Title:** [exact title from data]
- **Word Count:** [exact count from data]
- **Current H1:** [exact H1 from data, or "MISSING"]
- **Current H2s:** [exact H2s from data]
- **Meta Description:** [present/missing, from data]
- **Issues:**
  - [Specific issues found in the data]
- **Recommended Fixes:**
  - [Content additions, heading restructure, meta improvements]

### 🔴 Pages Needing Rewrites
Very thin pages, pages with no structure, or pages with serious issues:
- What's wrong and what a rewrite should include

### 📄 Suggested New Pages
Based on the business type and content gaps visible in the crawl:
- What pages are missing that competitors likely have
- Suggested title and heading structure for each
- Mark these clearly as RECOMMENDATIONS, not findings

IMPORTANT: When listing suggested new pages, clearly state these are recommendations 
based on industry best practices, NOT data findings from the crawl.

---

# 📝 CONTENT ANALYSIS

### Content Quality Assessment
- Average word count (cite exact number from data)
- Content depth distribution
- Content structure quality (heading usage patterns across pages)

### Content Gaps
- Important topics for this business type that have no dedicated page
- FAQ/educational content opportunities

### Heading & Intent Analysis
- Are H1/H2 tags optimized for likely search queries?
- Are headings structured for featured snippets and AI Overviews?

---

# 🤖 AEO READINESS SCORE

### Current AEO Status
- Content structure suitability for AI extraction
- Direct answer formatting
- List/table usage
- FAQ content presence

### AEO Score: **[Score]/10** with justification citing specific pages and data

---

# 📍 LOCAL SEO SIGNALS

(Only if the site shows local business indicators in the crawl data)
- Location pages present? (cite specific pages)
- LocalBusiness schema (cite from data)
- Contact information visibility
- NAP consistency on the site

---

# 💡 OPPORTUNITY ANALYSIS

### If This Is a Potential Client
- Top 5 quick wins based on actual issues found in the data
- SEO maturity level (1-10) justified by data
- Revenue opportunity areas

### If This Is a Competitor
- Their strengths to match or exceed (cite specific pages/features)
- Their weaknesses to exploit (cite specific data points)
- Content opportunities they're missing

---

# 🎯 PRIORITIZED RECOMMENDATIONS

| Priority | Action | Affected Page(s) | Effort | Expected Impact |
|----------|--------|-------------------|--------|-----------------|

Include 15-20 specific, actionable items sorted by impact.
Every item MUST reference specific pages or data from the crawl.

---

# 🤝 Hans' Section

This section is the executive brief — written in plain, non-technical language that anyone 
can understand. Think of it as what you'd say if you were sitting across the table from 
the client (or pitching your services to this prospect).

### The Headline
Open with the single most important finding — either the biggest opportunity or the most 
critical problem. Keep it to 1-2 sentences that would make a business owner lean in.

### Why This Matters
Translate the technical findings into business impact. Avoid SEO jargon entirely. 
Frame everything in terms of:
- Traffic and visibility ("people finding your business")
- Leads and customers ("turning visitors into calls/bookings")
- Revenue and growth ("what this means for your bottom line")
- Competitive positioning ("how you compare to others in your market")

Keep this to 2-3 paragraphs max.

### The Bottom Line
End with a concise 1-2 sentence summary that could be used as a pitch or relay statement. 
This should be powerful enough to text to someone or use in a sales conversation.

Example tone: "Their website has strong bones, but they're invisible on [X]. There's a 
clear opportunity to capture [Y] traffic that their competitors are getting. With the right 
fixes, this site could be a lead generation machine within 90 days."

---

FORMATTING RULES:
1. Reference actual pages, headings, and content found during the crawl
2. Quantify everything (word counts, page counts, % of pages with issues)
3. Make it presentation-ready for a client pitch or competitive report
4. Include both SEO and AEO angles for every recommendation
5. If data is insufficient for a section, state that clearly — do NOT guess
6. In tables, use SHORT page slugs (e.g. `/services`, `/about`) — NOT full URLs. If listing multiple pages, separate with commas. Max 3 pages per cell; if more, say "+ N others"

## CONFIDENCE TAGGING (Internal Use Only)

Every factual claim, finding, or recommendation MUST have a confidence tag at the end of the sentence or bullet point. Use these exact tags:

- `[DATA]` — This finding comes directly from the collected crawl data (page titles, word counts, status codes, headings). Example: "The homepage title is 'Welcome' — a generic title that provides no keyword signal [DATA]"
- `[INFERRED]` — This is a reasonable conclusion drawn from the data, but not a direct measurement. Example: "The lack of FAQ content means this site is unlikely to appear in AI-generated answers [INFERRED]"
- `[ESTIMATED]` — This is your professional judgment, projection, or estimate not directly supported by the data. Example: "Adding structured FAQ pages could capture an estimated 500+ monthly searches [ESTIMATED]"

Rules:
- Every bullet point in findings, recommendations, and tables MUST end with one of these tags
- If a sentence contains multiple claims, tag the dominant claim type
- The Hans' Section does NOT get confidence tags (it's meant to be conversational)
- Be honest — do NOT tag an estimate as [DATA]
- When in doubt between [INFERRED] and [ESTIMATED], use [ESTIMATED]
"""


def format_gsc_context(gsc_data: dict) -> str:
    """Format GSC data into a readable context block.

    Prominently features TRUE site-wide totals and expands query coverage
    to give the AI as much data as possible for the consultative narrative.
    """
    if not gsc_data:
        return "No GSC data available."

    summary = gsc_data.get("summary", {})

    # ── TRUE SITE-WIDE TOTALS (most important — always show first) ────────
    lines = [
        "### Google Search Console Data",
        "",
        "#### ⭐ SITE-WIDE TOTALS (TRUE aggregate — use these as the headline numbers):",
        f"- **Total Impressions (site-wide): {summary.get('total_impressions', 0):,}**",
        f"- **Total Clicks (site-wide): {summary.get('total_clicks', 0):,}**",
        f"- **Average CTR: {summary.get('avg_ctr', 0)}%**",
        f"- **Average Position: {summary.get('avg_position', 0)}**",
        "",
        f"- Unique Queries Tracked: {summary.get('total_queries', 0):,}",
        f"- Pages Receiving Traffic: {summary.get('total_pages', 0):,}",
        f"- Query Breakdown Coverage: {summary.get('query_coverage_pct', 0)}% of total impressions",
        f"- Sitemaps: {summary.get('sitemap_count', 0)}",
        "",
        "NOTE: The site-wide totals above are the TRUE numbers from a dimensionless",
        "GSC query. The query breakdown below covers the top queries by volume.",
        "Always use the site-wide totals for headline figures in the report.",
        "",
    ]

    # ── ALL SEARCH QUERIES (expanded to top 100) ─────────────────────────
    queries = gsc_data.get("queries")
    if queries is not None and not queries.empty:
        lines.append(f"#### Search Queries This Site Appears For (Top {min(len(queries), 100)}):")
        for _, row in queries.head(100).iterrows():
            # Flag CTR performance tier
            ctr = row['ctr']
            if ctr < 1.0:
                tier = "🔴"
            elif ctr < 3.0:
                tier = "🟡"
            else:
                tier = "🟢"
            lines.append(
                f"  - {tier} \"{row['query']}\" — Clicks: {row['clicks']}, "
                f"Impressions: {row['impressions']:,}, "
                f"CTR: {ctr}%, Position: {row['position']}"
            )
        lines.append("")
        lines.append(f"  (Showing top {min(len(queries), 100)} of {len(queries):,} tracked queries)")
        lines.append("")

    # ── TOP PAGES ─────────────────────────────────────────────────────────
    pages = gsc_data.get("pages")
    if pages is not None and not pages.empty:
        lines.append("#### Top 30 Pages by Clicks:")
        for _, row in pages.head(30).iterrows():
            lines.append(
                f"  - {row['page']} — Clicks: {row['clicks']}, "
                f"Impressions: {row['impressions']:,}, "
                f"CTR: {row['ctr']}%, Position: {row['position']}"
            )
        lines.append("")

    # ── STRIKING DISTANCE ─────────────────────────────────────────────────
    striking = gsc_data.get("striking_distance")
    if striking is not None and not striking.empty:
        lines.append("#### Striking Distance Keywords (Position 11-20):")
        for _, row in striking.head(30).iterrows():
            lines.append(
                f"  - \"{row['query']}\" — Position: {row['position']}, "
                f"Impressions: {row['impressions']:,}, Clicks: {row['clicks']}"
            )
        lines.append("")

    # ── LOW CTR OPPORTUNITIES (expanded to 50) ────────────────────────────
    low_ctr = gsc_data.get("low_ctr_opportunities")
    if low_ctr is not None and not low_ctr.empty:
        lines.append(f"#### 🔴 Low CTR Opportunities (high impressions, <3% CTR) — {len(low_ctr)} queries:")
        for _, row in low_ctr.head(50).iterrows():
            lines.append(
                f"  - \"{row['query']}\" — Impressions: {row['impressions']:,}, "
                f"CTR: {row['ctr']}%, Position: {row['position']}, Clicks: {row['clicks']}"
            )
        lines.append("")

    # ── SITEMAPS ───────────────────────────────────────────────────────────
    sitemaps = gsc_data.get("sitemaps", [])
    if sitemaps:
        lines.append("#### Submitted Sitemaps:")
        for sm in sitemaps:
            status = "⚠️ Pending" if sm.get("isPending") else "✅ Processed"
            errors = sm.get("errors", 0)
            lines.append(f"  - {sm['path']} — {status}, Errors: {errors}")
        lines.append("")

    return "\n".join(lines)


def format_bing_context(bing_data: dict) -> str:
    """Format Bing data into a readable context block."""
    if not bing_data:
        return "No Bing Webmaster data available."

    summary = bing_data.get("summary", {})
    lines = [
        "### Bing Webmaster Tools Data",
        f"- Total Clicks (Bing): {summary.get('total_clicks', 0):,}",
        f"- Total Impressions (Bing): {summary.get('total_impressions', 0):,}",
        f"- Tracked Queries: {summary.get('total_queries', 0)}",
        f"- Pages Crawled: {summary.get('pages_crawled', 0)}",
        f"- Crawl Errors: {summary.get('crawl_errors', 0)}",
        "",
    ]

    queries = bing_data.get("queries")
    if queries is not None and not queries.empty:
        lines.append("#### Top Bing Queries:")
        for _, row in queries.head(20).iterrows():
            lines.append(
                f"  - \"{row['query']}\" — Clicks: {row['clicks']}, "
                f"Impressions: {row['impressions']:,}, Position: {row['position']}"
            )
        lines.append("")

    crawl = bing_data.get("crawl_stats", {})
    if crawl.get("data"):
        lines.append("#### Recent Crawl Activity (Last 7 Days):")
        for day in crawl["data"][-5:]:
            lines.append(f"  - Crawled: {day.get('CrawledPages', 0)} pages")
        lines.append("")

    return "\n".join(lines)


def format_crawl_context(crawl_data: dict) -> str:
    """Format crawler data into a detailed context block."""
    if not crawl_data:
        return "No crawl data available."

    summary = crawl_data.get("summary", {})
    tech = crawl_data.get("technical_seo")

    lines = [
        "### Site Crawl Data",
        f"- Pages Crawled: {summary.get('pages_crawled', 0)}",
        f"- Total Word Count: {summary.get('total_word_count', 0):,}",
        f"- Avg Word Count/Page: {summary.get('avg_word_count', 0)}",
        f"- Pages with Meta Description: {summary.get('pages_with_meta_description', 0)}",
        f"- Pages with H1: {summary.get('pages_with_h1', 0)}",
        f"- Pages with Schema Markup: {summary.get('pages_with_schema', 0)}",
        f"- Schema Types Found: {', '.join(summary.get('schema_types_found', [])) or 'None'}",
        f"- Total Images: {summary.get('total_images', 0)}",
        f"- Images Without Alt: {summary.get('images_without_alt', 0)}",
        f"- HTTPS: {'Yes' if summary.get('uses_https') else 'No'}",
        f"- Sitemap: {'Found' if summary.get('has_sitemap') else 'Not Found'}",
        f"- Robots.txt: {'Found' if summary.get('has_robots_txt') else 'Not Found'}",
        f"- Mobile Viewport: {'Yes' if summary.get('has_viewport_meta') else 'No'}",
        f"- Avg Load Time: {summary.get('avg_load_time', 0)}s",
        f"- Crawl Errors: {summary.get('crawl_errors', 0)}",
        "",
    ]

    # Page-by-page breakdown — include ALL pages for content audit
    pages = crawl_data.get("pages", [])
    pages_missing_h1 = []
    pages_missing_meta = []

    if pages:
        lines.append("#### Page-by-Page Breakdown:")
        for page in pages[:50]:  # Up to 50 pages for thorough audit
            # Determine H1 status with clear markers
            if page.h1 and page.h1[0].strip():
                h1_text = page.h1[0].strip()
                if h1_text.startswith("[JS-rendered"):
                    h1_display = f"⚠️ {h1_text}"
                else:
                    h1_display = f"✅ PRESENT: \"{h1_text}\""
            else:
                h1_display = "❌ MISSING"
                pages_missing_h1.append(page.url)

            # Determine meta description status
            if page.meta_description and page.meta_description.strip():
                meta_display = f"✅ PRESENT: \"{page.meta_description[:200].strip()}\""
            else:
                meta_display = "❌ MISSING"
                pages_missing_meta.append(page.url)

            schema_text = ", ".join(page.schema_types) if page.schema_types else "None"
            h2_list = ", ".join(page.h2[:8]) if page.h2 else "None"

            lines.extend([
                f"\n**{page.url}** (Status: {page.status_code})",
                f"  - Title: {page.title or '❌ MISSING'}",
                f"  - Meta Description: {meta_display}",
                f"  - H1: {h1_display}",
                f"  - H2s: {h2_list}",
                f"  - Word Count: {page.word_count}",
                f"  - Internal Links: {page.internal_links}, External: {page.external_links}",
                f"  - Images: {page.total_images} (without alt: {page.images_without_alt})",
                f"  - Schema: {schema_text}",
                f"  - Load Time: {page.load_time}s",
            ])
        lines.append("")

        # Add verification summary — this is the DEFINITIVE list
        lines.append("#### ⚠️ VERIFICATION SUMMARY (use this as the source of truth):")
        lines.append("")

        if pages_missing_h1:
            lines.append(f"Pages with MISSING H1 ({len(pages_missing_h1)} total):")
            for url in pages_missing_h1:
                lines.append(f"  - {url}")
        else:
            lines.append("Pages with MISSING H1: NONE — all pages have H1 tags.")

        lines.append("")

        if pages_missing_meta:
            lines.append(f"Pages with MISSING Meta Description ({len(pages_missing_meta)} total):")
            for url in pages_missing_meta:
                lines.append(f"  - {url}")
        else:
            lines.append("Pages with MISSING Meta Description: NONE — all pages have meta descriptions.")

        lines.append("")

    return "\n".join(lines)
