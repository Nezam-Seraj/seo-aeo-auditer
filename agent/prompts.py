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
    """
    return f"""You are a Senior SEO & AEO (Answer Engine Optimization) Strategist performing a 
comprehensive site analysis with a deep content audit. You have access to REAL data from 
Google Search Console, Bing Webmaster Tools, and a full site crawl.

{_ANTI_HALLUCINATION_RULES}

## DATA SOURCES

{data_context}

## ANALYSIS FRAMEWORK

Produce a comprehensive report with these sections:

---

# 📊 EXECUTIVE SUMMARY

Provide a 3-4 paragraph overview covering:
- Overall site health and performance trajectory
- Top 3 strengths (backed with specific data from above)
- Top 3 critical issues (backed with specific data from above)
- Content audit verdict: overall content health rating

---

# 🔧 TECHNICAL SEO AUDIT

### Indexation & Crawlability
- Sitemap status and coverage
- Crawl stats from Bing (pages crawled, error rates) — cite exact numbers from data
- Any indexation issues visible in the data

### Site Performance
- Page load indicators from crawl data (cite actual avg load time)
- Mobile readiness signals (viewport meta presence)
- HTTPS status

### Structured Data
- Schema types found (list exactly what was found in the crawl data)
- Missing schema opportunities based on the business type

For each issue found, provide:
- **Issue:** [What's wrong — cite the specific data]
- **Impact:** [High/Medium/Low]
- **Fix:** [Specific recommendation]

---

# 📋 PAGE-LEVEL CONTENT AUDIT

This is the most important section. For EVERY page found in the crawl data, provide a content 
assessment. Group pages by quality tier:

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

# 📝 CONTENT & ON-PAGE SEO

### Top Performing Content
- Which pages/queries drive the most traffic (cite exact GSC data)
- What's working and should be replicated

### Striking Distance Opportunities
- Keywords ranking positions 11-20 (page 2 of Google)
- For each: exact current position, impressions, and specific action to move to page 1
- Reference the actual URL that ranks for each keyword

### Low CTR Opportunities
- Pages/queries with high impressions but low CTR
- For each: cite exact impression count, CTR, and position from the data
- Recommend specific meta title/description improvements

### Heading & Structure Analysis
- H1/H2 hierarchy issues found during crawl (reference specific pages)
- Pages missing meta descriptions (list them by URL)

For each recommendation, explain:
- **Why (SEO):** How this improves Google rankings
- **Why (AEO):** How this helps with AI Overview citations

---

# 🤖 AEO READINESS ASSESSMENT

### AI Overview Eligibility
- Which pages have content structured for AI extraction (direct answers, lists, tables)
- Content that could be cited by AI assistants

### AEO Optimization Opportunities
- Content restructuring needed for AI citation eligibility
- Question-based heading opportunities (based on actual queries in the data)
- Schema markup improvements for AI understanding

### AEO Score: **[Score]/10** with justification based on the data

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

# 🎯 PRIORITIZED ACTION PLAN

Create a table with columns:
| Priority | Action | Page/Query | Effort | Expected Impact | Timeline |

Sort by impact, then effort (quick wins first). Include:
- **Quick Wins** (< 1 week, high impact)
- **Medium-Term** (1-4 weeks)  
- **Long-Term** (1-3 months)

Every action MUST reference a specific page URL or query from the data above.

---

# 🤝 Hans' Section

This section is the executive brief — written in plain, non-technical language that anyone 
can understand. Think of it as what you'd say if you were sitting across the table from 
the client (or relaying this to a prospect over the phone).

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

Example tone: "Your website has a solid foundation, but you're leaving money on the table 
with [X]. Fixing [Y] and [Z] could realistically increase your organic traffic by [est. %] 
within 3 months."

---

IMPORTANT FORMATTING RULES:
1. Use markdown formatting with clear headers
2. Include specific data points — never give vague advice
3. Every recommendation must reference the actual data that supports it
4. Be actionable — say exactly what to do, not just what's wrong
5. If you don't have enough data for a section, say "Insufficient data" — do NOT fabricate
6. In tables, use SHORT page slugs (e.g. `/services`, `/about`) — NOT full URLs. If listing multiple pages, separate with commas. Max 3 pages per cell; if more, say "+ N others"

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
    """Format GSC data into a readable context block."""
    if not gsc_data:
        return "No GSC data available."

    summary = gsc_data.get("summary", {})
    lines = [
        "### Google Search Console Data",
        f"- Total Clicks: {summary.get('total_clicks', 0):,}",
        f"- Total Impressions: {summary.get('total_impressions', 0):,}",
        f"- Average CTR: {summary.get('avg_ctr', 0)}%",
        f"- Average Position: {summary.get('avg_position', 0)}",
        f"- Tracked Queries: {summary.get('total_queries', 0)}",
        f"- Tracked Pages: {summary.get('total_pages', 0)}",
        f"- Sitemaps: {summary.get('sitemap_count', 0)}",
        "",
    ]

    # Top queries
    queries = gsc_data.get("queries")
    if queries is not None and not queries.empty:
        lines.append("#### Top 30 Queries:")
        for _, row in queries.head(30).iterrows():
            lines.append(
                f"  - \"{row['query']}\" — Clicks: {row['clicks']}, "
                f"Impressions: {row['impressions']:,}, "
                f"CTR: {row['ctr']}%, Position: {row['position']}"
            )
        lines.append("")

    # Top pages
    pages = gsc_data.get("pages")
    if pages is not None and not pages.empty:
        lines.append("#### Top 20 Pages:")
        for _, row in pages.head(20).iterrows():
            lines.append(
                f"  - {row['page']} — Clicks: {row['clicks']}, "
                f"Impressions: {row['impressions']:,}, "
                f"CTR: {row['ctr']}%, Position: {row['position']}"
            )
        lines.append("")

    # Striking distance
    striking = gsc_data.get("striking_distance")
    if striking is not None and not striking.empty:
        lines.append("#### Striking Distance Keywords (Position 11-20):")
        for _, row in striking.head(20).iterrows():
            lines.append(
                f"  - \"{row['query']}\" — Position: {row['position']}, "
                f"Impressions: {row['impressions']:,}, Clicks: {row['clicks']}"
            )
        lines.append("")

    # Low CTR opportunities
    low_ctr = gsc_data.get("low_ctr_opportunities")
    if low_ctr is not None and not low_ctr.empty:
        lines.append("#### Low CTR Opportunities (high impressions, <3% CTR):")
        for _, row in low_ctr.head(15).iterrows():
            lines.append(
                f"  - \"{row['query']}\" — Impressions: {row['impressions']:,}, "
                f"CTR: {row['ctr']}%, Position: {row['position']}"
            )
        lines.append("")

    # Sitemaps
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
