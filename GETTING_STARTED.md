# SEO/AEO Analyzer — Getting Started

## What You Need (One-Time)

1. **Python 3.10+** — Download from [python.org/downloads](https://www.python.org/downloads/)
   > ⚠️ During installation, **check the box** that says **"Add Python to PATH"** — this is critical.

2. **Gemini API Key** — Free from [Google AI Studio](https://aistudio.google.com/apikey)

3. **Bing API Key** — From [Bing Webmaster Tools](https://www.bing.com/webmasters) (optional)

4. **credentials.json** — Ask Nezam for this file (needed for Client Mode only)

---

## First-Time Setup (5 minutes)

1. Download or clone this project to your Desktop
2. Drop `credentials.json` into the project folder
3. Double-click **`SETUP.bat`**
4. Enter your API keys when prompted
5. Done! ✅

---

## Running the App (Every Time)

1. Double-click **`START_APP.bat`**
2. The app opens automatically in your browser
3. To stop: just close the black terminal window

---

## Two Analysis Modes

### 👤 Client Analysis
For existing clients whose Google accounts you can access. Pulls real data from:
- Google Search Console
- Bing Webmaster Tools
- Site crawl data

**First time:** A Google login popup will appear — sign in with the account that has access to the client's GSC property.

### 🔍 Prospect / Competitor Analysis
For new leads or competitors. Just enter their website URL — no logins needed.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "Python is not installed" | Install from [python.org](https://www.python.org/downloads/) — check "Add to PATH" |
| App won't open in browser | Go to http://localhost:8501 manually |
| "Please provide a Gemini API key" | Click the sidebar, enter your key (or re-run SETUP.bat) |
| Google login popup doesn't appear | Delete `token.json` from the project folder and restart |
| App shows a red error | Close the app, double-click START_APP.bat again |

---

*Questions? Ask Nezam.*
