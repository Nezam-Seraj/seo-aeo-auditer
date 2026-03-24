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
