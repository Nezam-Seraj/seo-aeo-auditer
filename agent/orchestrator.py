"""
orchestrator.py — Gemini-Powered Analysis Agent

Orchestrates data collection and AI analysis for both Client and Prospect modes.
Acts as the central brain that:
1. Collects data from all relevant sources
2. Assembles a unified context
3. Sends to Gemini for deep analysis
4. Returns a structured report
"""

from google import genai

from config import GEMINI_MODEL
from agent.prompts import (
    build_client_analysis_prompt,
    build_prospect_analysis_prompt,
    format_gsc_context,
    format_bing_context,
    format_crawl_context,
)


def run_client_analysis(
    gsc_data: dict = None,
    bing_data: dict = None,
    crawl_data: dict = None,
    api_key: str = "",
    model: str = GEMINI_MODEL,
) -> str:
    """
    Run a full client analysis using all available platform data.

    Assembles context from GSC, Bing, and crawl data and sends to Gemini
    for comprehensive analysis with page-level content audit.

    Returns the full analysis report as markdown.
    """
    # Assemble context from all data sources
    context_parts = []

    if gsc_data:
        context_parts.append(format_gsc_context(gsc_data))
    if bing_data:
        context_parts.append(format_bing_context(bing_data))
    if crawl_data:
        context_parts.append(format_crawl_context(crawl_data))

    if not context_parts:
        return "❌ No data available for analysis. Please ensure at least one data source is connected."

    data_context = "\n\n---\n\n".join(context_parts)
    prompt = build_client_analysis_prompt(data_context)

    # Send to Gemini
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text


def run_prospect_analysis(
    crawl_data: dict,
    api_key: str = "",
    model: str = GEMINI_MODEL,
) -> str:
    """
    Run a prospect/competitor analysis using only crawled data.

    Returns the full competitive analysis report as markdown.
    """
    crawl_context = format_crawl_context(crawl_data)
    prompt = build_prospect_analysis_prompt(crawl_context)

    # Send to Gemini
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text


def generate_client_facing_report(
    internal_report: str,
    site_url: str,
    api_key: str = "",
    model: str = GEMINI_MODEL,
) -> str:
    """
    Transform the internal analysis report into a polished, client-facing deliverable.

    Takes the full internal report and rewrites it as a professional document
    suitable for sending directly to a client or prospect.
    """
    prompt = f"""You are a professional SEO consultant preparing a deliverable report for a client.

Below is your internal analysis of {site_url}. Rewrite it as a polished, client-facing report
that you would be proud to put your name on and send directly to a business owner.

## INTERNAL ANALYSIS (do NOT include this raw data in the deliverable):

{internal_report}

## YOUR TASK:

Rewrite the above analysis into a professional client deliverable. The report must follow
a CONSULTATIVE SALES NARRATIVE — not a generic audit dump.

### Narrative Arc:
The report should tell this story: "You already have massive visibility → but people
aren't clicking → here's why → here's exactly how we fix it → here's the timeline."

### Structure:

1. **Your Search Visibility** — Open with the BIG impressive number of total impressions.
   Frame it as validation: "Google already considers you relevant for [X] searches."
   Show some of the specific search queries they appear for so the client can see real data.
   This must feel like a WIN — they already have a strong foundation.

2. **The Opportunity** — Pivot to the gap. Show that despite massive visibility, the
   click-through rate is low. Quantify what they're leaving on the table.
   "Of those [X] search appearances, only [Y] resulted in actual visits."
   Make this feel urgent but solvable — it's a missed opportunity, not a failure.

3. **What's Changed** — Briefly explain (in plain language) that search is evolving.
   AI-powered search features now answer many queries directly, which means fewer people
   click through to websites. Frame this as an industry-wide shift, not their fault.
   But — businesses that adapt actually benefit MORE from AI search.

4. **Our Strategy** — Present the solution plan:
   - Optimizing website structure and page titles to win more clicks
   - Adding technical signals (don't call it "schema" — say "structured data that helps
     search engines understand your business better")
   - Restructuring content so your business gets featured in AI-powered search results
   - Specific pages and elements that need attention (reference actual pages from the data)

5. **Implementation Roadmap** — A clean, phased timeline:
   | Phase | What We'll Do | Expected Impact | Timeline |
   - Phase 1: Quick Wins (Week 1-2)
   - Phase 2: Content & Structure (Month 1)
   - Phase 3: Growth & Expansion (Month 2-3)

6. **Expected Results** — Realistic projections of what they can expect to see and when.
   Frame in terms of business outcomes (more visitors, better engagement), not metrics.

7. **Next Steps** — 2-3 concrete next steps, framed as an invitation to work together.

### Tone & Style Rules:
- Professional but approachable — like a trusted advisor, not a textbook
- ZERO technical jargon (no "crawl budget," "canonical tags," "schema markup" etc.)
- Frame everything as business impact, not technical issues
- Be specific — reference actual pages and findings from the data, but describe them naturally
- Use the business owner's perspective — "your homepage," "your services page"
- Be honest about issues but constructive — problems are "opportunities"
- Do NOT include raw data tables, query lists, or metrics dumps
- Do NOT include the Hans' Section — that was for internal use
- Do NOT include ANY confidence tags like [DATA], [INFERRED], or [ESTIMATED] — those are internal only
- Do NOT mention "AI Overview," "AEO," or "Answer Engine" — instead say things like
  "visibility in AI-powered search results" or "appearing in smart search features"
- ALWAYS lead with the big visibility number — it's the hook that makes clients lean in

### Formatting:
- Clean markdown with clear headers
- Use emojis sparingly and professionally (✅, ⚠️, 📊 are fine)
- Keep it concise — aim for a report that takes 5-7 minutes to read
- No section should be longer than 1 page when printed
"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text
