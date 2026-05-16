# Job Scraper

Scrapers for multiple Indian government job portals. Data is stored in Supabase.

## Features
- Runs all scrapers in one command
- Optional daily scheduler for midnight runs
- Playwright-based scraping with headless support

## Requirements
- Python 3.11+
- Supabase credentials in environment variables

## Setup
1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m playwright install --with-deps
   ```

2. Create a `.env` file with:
   ```bash
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   ```

## Run locally
- Run once:
  ```bash
  python main.py
  ```

- Run daily at midnight (local time):
  ```bash
  python main.py --daemon
  ```

## GitHub Actions (daily at midnight IST)
The workflow is defined in `.github/workflows/daily-scrapers.yml`. Add these repo secrets:
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Notes
- Set `HEADLESS=false` to open a browser window during debugging.
