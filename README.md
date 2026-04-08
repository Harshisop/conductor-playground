# Job Scraper

Automated multi-user job scraper with a registration website. Scrapes LinkedIn, Indeed, Naukri, Google Jobs, Remotive, and Himalayas — pushes results to per-user Google Sheet tabs every 3 days via GitHub Actions.

## How It Works

1. Users register via a **GitHub Pages website** (name, keywords, locations, sources, job type)
2. Registration is saved to a **"Users" tab** in Google Sheets via Google Apps Script
3. Every 3 days, GitHub Actions reads all registered users and **scrapes jobs for each one**
4. Results are **deduplicated** and pushed to **per-user tabs** (e.g., "Harsh Mamgain")
5. Max **5 users** supported

## Setup

### 1. Google Cloud Service Account (free)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Go to **Credentials** → Create **Service Account** → download JSON key

### 2. Google Sheet

1. Create a Google Sheet named **"Job Scraper Results"**
2. Share it with the service account email (from JSON key) as **Editor**

### 3. GitHub Secrets

Add secret `GOOGLE_SHEETS_CREDS_JSON` with the JSON key contents:
**Settings → Secrets and variables → Actions → New repository secret**

### 4. Google Apps Script (form backend)

1. Go to [script.google.com](https://script.google.com/) → New Project
2. Paste the code from `apps-script/Code.js`
3. Replace `SPREADSHEET_ID` with your Google Sheet ID (from the sheet URL)
4. Click **Deploy → New Deployment → Web App**
   - Execute as: **Me**
   - Access: **Anyone**
5. Copy the deployment URL

### 5. Update the Website

1. Open `docs/script.js`
2. Replace `PASTE_YOUR_APPS_SCRIPT_URL_HERE` with the Apps Script deployment URL

### 6. Enable GitHub Pages

1. Go to repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**, Folder: **/docs**
4. Save

### 7. Push and Go

Push the code. The scraper runs every 3 days automatically, or trigger manually from **Actions → Job Scraper → Run workflow**.

## Project Structure

```
├── config.yaml                  # Base settings + fallback search config
├── requirements.txt
├── docs/                        # GitHub Pages registration site
│   ├── index.html
│   ├── style.css
│   └── script.js
├── apps-script/
│   └── Code.js                  # Google Apps Script (deploy via script.google.com)
├── src/
│   ├── main.py                  # Multi-user orchestrator
│   ├── config_loader.py         # Config parser
│   ├── models.py                # JobListing + UserConfig models
│   ├── dedup.py                 # Deduplication logic
│   ├── user_config.py           # UserConfig → SearchConfig conversion
│   ├── scrapers/
│   │   ├── jobspy_scraper.py    # LinkedIn, Indeed, Naukri, Google Jobs
│   │   ├── remotive_api.py      # Remotive free API
│   │   └── himalayas_api.py     # Himalayas free API
│   └── sheets/
│       └── google_sheets.py     # Google Sheets read/write
└── .github/workflows/
    └── scrape.yml               # GitHub Actions cron workflow
```

## Local Testing

```bash
pip install -r requirements.txt
export GOOGLE_SHEETS_CREDS_JSON='<contents of your service account JSON>'
python -m src.main
```

## Notes

- If no users are registered, the scraper falls back to `config.yaml` searches
- LinkedIn may block GitHub Actions IPs occasionally — the scraper handles this gracefully
- Keep the repo **public** for unlimited free GitHub Actions minutes
- If Google Sheets push fails, backup CSVs are saved as GitHub Actions artifacts
