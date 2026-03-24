# SEO/AEO Analyzer — Data Validation Checklist

Use this checklist after every analysis to verify that the data and AI recommendations
are accurate and not hallucinated. **Real data comes from APIs; only the analysis text is AI-generated.**

---

## Understanding What's Real vs AI-Generated

| Component | Source | Can Hallucinate? |
|---|---|---|
| GSC queries, clicks, impressions, CTR, position | Google Search Console API | ❌ No — raw API data |
| GA4 sessions, users, bounce rate, landing pages | GA4 Data API | ❌ No — raw API data |
| GBP locations, reviews, ratings | GBP API | ❌ No — raw API data |
| Bing queries, crawl stats | Bing Webmaster API | ❌ No — raw API data |
| Crawled page data (headings, meta, word count) | Direct HTTP crawl | ❌ No — scraped from live site |
| **Analysis report text** | **Gemini AI** | **⚠️ Possible** — verify claims |

> The AI receives **real data** and writes an analysis based on it.
> The risk is the AI misinterpreting data, inventing trends, or citing numbers that don't match the source.

---

## 1. GSC Data Validation

Open your property in [Google Search Console](https://search.google.com/search-console) → **Performance** → Last **90 days**

- [ ] **Total Clicks** in the report ≈ GSC total (within ~5%)
- [ ] **Total Impressions** ≈ GSC total
- [ ] Top 5 queries listed in the report actually appear in GSC
- [ ] Striking distance keywords (pos 11-20) are genuinely in that range in GSC
- [ ] Page URLs mapped to queries match what GSC shows under **Pages** tab
- [ ] Sitemap count matches what's in GSC → **Sitemaps** section

### How to spot-check a query:
1. Pick any query from the report
2. Search for it in GSC → Performance → filter by that query
3. Compare clicks, impressions, and position

> **Minor differences are normal** — GSC UI rounds differently than the API.

---

## 2. GA4 Data Validation

Open [Google Analytics](https://analytics.google.com) → Select your property → Last **90 days**

- [ ] **Sessions** count ≈ GA4 dashboard total
- [ ] **Total Users** ≈ GA4 dashboard
- [ ] **Bounce Rate** is in a realistic range (not 0% or 99%)
- [ ] Top landing pages match what GA4 shows under **Engagement** → **Landing pages**
- [ ] Traffic source breakdown matches **Acquisition** → **Traffic acquisition**
- [ ] Device split (mobile/desktop/tablet) matches GA4 **Tech** → **Overview**

---

## 3. GBP Data Validation

Open [Google Business Profile](https://business.google.com)

- [ ] Business name and category match your GBP listing
- [ ] Address shown is correct
- [ ] Average rating matches your GBP dashboard
- [ ] Review count is in the right ballpark

---

## 4. Bing Data Validation

Open [Bing Webmaster Tools](https://www.bing.com/webmasters)

- [ ] Top queries in the report exist in Bing's **Search Performance** section
- [ ] Click/impression counts are in the right range
- [ ] Crawl stats (pages crawled, errors) match Bing's **Site Activity** tab

---

## 5. Crawl Data Validation (Client & Prospect Mode)

- [ ] Pages crawled count is reasonable (not 0 or an impossibly high number)
- [ ] Page titles match what you see when visiting those URLs
- [ ] Word counts seem reasonable for each page
- [ ] Schema types found actually exist on the site (View Source → search for `ld+json`)
- [ ] HTTPS/robots.txt/sitemap status matches reality

### Quick crawl verification:
1. Pick 2-3 pages from the crawl report
2. Visit them in a browser
3. Right-click → View Source → confirm title, meta description, H1 tags match

---

## 6. AI Analysis Validation (Most Important!)

This is where hallucinations are most likely. Check these:

### Numbers & Claims
- [ ] Any specific number cited in the analysis (e.g., "your CTR is 2.3%") matches the raw data shown above it
- [ ] Percentages and comparisons ("your bounce rate is high at 85%") match actual GA4 data
- [ ] If the AI says "X query has Y impressions" — verify against the GSC table

### Recommendations
- [ ] Recommendations reference pages/URLs that actually exist on the site
- [ ] Keywords mentioned in suggestions are real keywords from the data (not invented ones)
- [ ] "Missing page" suggestions aren't pages that already exist on the site
- [ ] Schema recommendations don't suggest adding schema types that are already present

### 🔴 Red Flags
- AI cites a specific metric that doesn't appear in any data source
- AI recommends optimizing a page URL that doesn't exist
- AI claims a ranking position that contradicts the GSC data
- Numbers in the Executive Summary don't match numbers in the detailed sections

### 🟢 Green Flags
- AI analysis directly references data points visible in the raw tables
- Recommendations are specific to this site (not generic SEO advice)
- Striking distance keywords cited in the report match the GSC data exactly

---

## Quick Spot-Check Process (5 minutes)

1. **Pick 3 queries** from the GSC data → verify in GSC UI
2. **Pick 2 pages** from the crawl → visit them, confirm titles/headings
3. **Pick 3 claims** from the AI analysis → trace each back to a data source
4. **Check the action plan** → verify every cited URL and keyword is real

If all checks pass → **Data is reliable** ✅
If any numbers don't match → the AI may have misread or interpolated data ⚠️
