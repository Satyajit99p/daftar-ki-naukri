from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from common.data_service import is_url_saved, save_job_opening
from urllib.parse import urljoin

from common.utils import parse_timestamp

BASE_URL = "https://opportunities.rbi.org.in/scripts"

def extract_rbi_pairs(soup):
    data = []
    current_date = None

    rows = soup.select("tr")

    for row in rows:
        tds = row.find_all("td")

        if not tds:
            continue

        td = tds[0]

        # ---- Case 1: Date row ----
        if "tableheader" in td.get("class", []):
            current_date = td.get_text(strip=True)
            continue

        # ---- Case 2: Link row ----
        if "link2" in td.get("class", []):
            a_tag = td.find("a", href=True)

            if a_tag:
                if not current_date:
                    print("WARNING: link without date:", a_tag.get_text(strip=True))
                    continue

                data.append({
                    "date": current_date,
                    "title": a_tag.get_text(strip=True),
                    "url": f"{BASE_URL}/{a_tag['href']}"
                })

    return data

def scrape():
    saved_count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        page_url = f"{BASE_URL}/vacancies.aspx"
        print("Opening RBI vacancies page")

        page.goto(page_url)

        # ---- Allow JS challenge to resolve ----
        page.wait_for_load_state("domcontentloaded")

        html = page.locator("tbody").inner_html()

        soup = BeautifulSoup(html, "html.parser")

        rbi_data = extract_rbi_pairs(soup)

        browser.close()

        for item in rbi_data:
            pdf_link = item["url"]
            notification_title = item["title"]
            notification_date = parse_timestamp(item["date"])

            if is_url_saved(pdf_link):
                print(f"Already saved in DB: {pdf_link}")
                continue

            save_job_opening(
                government_body="RBI",
                job_title=notification_title,
                job_tag=None,       
                posted_date=notification_date,
                deadline=None,
                url=pdf_link,
            )
            print (f"Saved to DB: {item['title']}")
            saved_count += 1

        print(f"RBI scraper saved {saved_count} records")


if __name__ == "__main__":
    scrape()