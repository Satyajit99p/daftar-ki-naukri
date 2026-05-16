import os

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

from common.data_service import is_url_saved, save_job_opening
from common.utils import parse_timestamp

BASE_URL = "https://opportunities.rbi.org.in/scripts"

HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"


def extract_rbi_pairs_playwright(page):
    data = []
    current_date = None

    rows = page.locator("tbody tr")
    count = rows.count()

    print(f"Total TR (live DOM): {count}")

    for i in range(count):
        row = rows.nth(i)

        td = row.locator("td").first

        if td.count() == 0:
            continue

        classes = td.get_attribute("class") or ""

        # ---- Case 1: Date row ----
        if "tableheader" in classes:
            current_date = td.inner_text().strip()
            continue

        # ---- Case 2: Link row ----
        if "link2" in classes:
            a_tag = td.locator("a")

            if a_tag.count() == 0:
                continue

            title = a_tag.inner_text().strip()
            href = a_tag.get_attribute("href")

            if not current_date:
                print("WARNING: link without date:", title)
                continue

            data.append({
                "date": current_date,
                "title": title,
                "url": urljoin(BASE_URL, href)
            })

    return data


def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(
                        headless=HEADLESS,
                        args=["--disable-blink-features=AutomationControlled"]
                    )

        context = browser.new_context(
            user_agent="Mozilla/5.0 ...",
            viewport={"width": 1280, "height": 800}
        )

        page = context.new_page()

        page_url = f"{BASE_URL}/vacancies.aspx"
        print("Opening RBI vacancies page")

        page.goto(page_url)

        # ---- Wait for full DOM ----
        page.wait_for_load_state("domcontentloaded")
        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(1000)
        
        wait_for_table_stable(page)
        print("Final TR count (Playwright):", page.locator("tbody tr").count())

        # ---- Extract directly from DOM ----
        rbi_data = extract_rbi_pairs_playwright(page)

        print(f"Extracted records: {len(rbi_data)}")

        browser.close()

    # ---- Save to DB ----
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

        print(f"Saved to DB: {notification_title}")

def wait_for_table_stable(page, timeout=30000):
    import time

    start = time.time()
    last_count = -1
    stable_cycles = 0

    while time.time() - start < timeout / 1000:
        count = page.locator("tbody tr").count()
        print("Current row count:", count)

        if count == last_count:
            stable_cycles += 1
        else:
            stable_cycles = 0

        if stable_cycles >= 3:  # stable for 3 cycles
            return count

        last_count = count
        page.wait_for_timeout(500)

    raise Exception("Table did not stabilize")

if __name__ == "__main__":
    scrape()