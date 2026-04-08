# 🔬 SEO/AEO Analyzer

A comprehensive site analysis tool powered by Gemini AI — using data from Google Search Console, GA4, Google Business Profile, and Bing Webmaster Tools.

## Features

- **Client Mode** — Connect your platforms (GSC, GA4, GBP, Bing) for a full data-driven analysis
- **Prospect/Competitor Mode** — Crawl any public site for a technical + content audit
- **AI-Powered Analysis** — Gemini AI generates actionable SEO/AEO recommendations
- **PDF & Markdown Export** — Download reports in both formats
- **Client-Facing Reports** — Generate polished, jargon-free reports for business owners

## Quick Start (Local)

1. **Clone the repo**
   ```bash
   git clone https://github.com/Nezam-Seraj/seo-aeo-auditer.git
   cd seo-aeo-auditer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys:
   - `GEMINI_API_KEY` — Get from [Google AI Studio](https://aistudio.google.com/apikey)
   - `BING_API_KEY` — Get from [Bing Webmaster Tools](https://www.bing.com/webmasters)

5. **Set up Google OAuth (Client Mode only)**
   - Create OAuth credentials in [Google Cloud Console](https://console.cloud.google.com)
   - Download `credentials.json` and place it in the project root
   - First run will prompt you to authenticate

6. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select this repo
4. Set **Main file path** to `app.py`
5. Add your API keys in **Advanced settings → Secrets**:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   BING_API_KEY = "your-bing-api-key"
   ```

> **Note:** Client Mode (Google OAuth) requires local authentication and works best when running locally. Prospect/Competitor Mode works fully on cloud deployments.

## Project Structure

```
├── app.py                  # Main Streamlit UI
├── config.py               # Configuration & secrets
├── auth.py                 # Google OAuth2 authentication
├── agent/
│   ├── orchestrator.py     # Gemini AI analysis orchestration
│   ├── prompts.py          # AI prompt templates
│   └── report.py           # Report formatting & export
├── collectors/
│   ├── gsc.py              # Google Search Console collector
│   ├── ga4.py              # Google Analytics 4 collector
│   ├── gbp.py              # Google Business Profile collector
│   ├── bing.py             # Bing Webmaster Tools collector
│   └── crawler.py          # Site crawler
├── utils/
│   └── helpers.py          # Utility functions
├── .streamlit/
│   └── config.toml         # Streamlit theme & server config
├── requirements.txt        # Python dependencies
├── UI_UX_QC.md             # QC testing protocol
└── DATA_VALIDATION.md      # Data accuracy checklist
```

## Security

- **Read-only** — This tool only reads data from connected platforms. No modifications are made.
- **API keys** are loaded from `.env` (local) or Streamlit secrets (cloud) — never hardcoded.
- `credentials.json`, `token.json`, and `.env` are gitignored.

---

Built by [Xpress Promotions Inc](https://www.xpresspromotion.com)
