import os
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

from common.data_service import is_url_saved, save_job_opening
from common.utils import parse_timestamp

URL = "https://www.isro.gov.in/ViewAllOpportunities.html"
BASE_URL = "https://www.isro.gov.in"

HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"

def parse_table(html):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    rows = soup.select("table tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        post = cols[1].get_text(strip=True)
        last_date = cols[4].get_text(strip=True)
        posted_date = cols[3].get_text(strip=True)

        posted_date = parse_timestamp(posted_date)
        last_date = parse_timestamp(last_date)

        view_url = None

        # Find button instead of <a>
        button = cols[5].find("button", onclick=True)

        if button:
            onclick = button.get("onclick", "")

            # Extract URL using regex
            match = re.search(r"window\.location\.href='([^']+)'", onclick)

            if match:
                relative_url = match.group(1)
                view_url = urljoin(BASE_URL, relative_url)

        data.append({
            "post": post,
            "last_date": last_date,
            "posted_date": posted_date,
            "url": view_url
        })

    return data


def scrape():
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")

        # while True:
        #     print("\n--- New Pagination Window ---")

        buttons = page.locator("a.page")
        count = buttons.count()
        end_page_num = 0

        for i in range(count):
            txt = buttons.nth(i).inner_text().strip()

            if txt.isdigit() and int(txt) > end_page_num:
                end_page_num = int(txt)

        for num in range(1, int(end_page_num) + 1):
            print(f"Scraping page {num}")

            try:
                page.locator(f"a.page[data-i='{num}']").click()
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Failed to click page {num}: {e}")
                continue

            html = page.content()
            page_data = parse_table(html)

            all_data.extend(page_data)

        browser.close()

        for item in all_data:
            try:
                pdf_link = item["url"]

                if pdf_link.startswith("http://"):
                    pdf_link = "https://" + pdf_link[len("http://"):]

                if is_url_saved(pdf_link):
                    print(f"Already saved in DB: {pdf_link}")
                    continue

                save_job_opening(
                    government_body="ISRO",
                    job_title=item["post"],
                    job_tag=None,
                    posted_date=item["posted_date"],
                    deadline=item["last_date"],
                    url=pdf_link,
                )

                print (f"Saved to DB: {item['post']}")

            except Exception as ex:
                print(f"Failed downloading: {pdf_link}")
                print(ex)

if __name__ == "__main__":
    scrape()