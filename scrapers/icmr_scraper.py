from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from common.data_service import is_url_saved, save_job_opening

BASE_URL = "https://www.icmr.gov.in/employment-opportunities"

def scrape():
    saved_count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page_url = f"{BASE_URL}"
        print(f"Opening ICMR vacancies page ")
        page.goto(page_url, wait_until="networkidle", timeout=120000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        spans = soup.find_all("span", class_="value title")
        vacancy_links = []

        for span in spans:
            text = span.get_text(strip=True).lower()

            if "advertisement" in text and "english" in text:
                parent_a = span.find_parent("a", href=True)

                opening_header = parent_a.get("aria-label", "").lower()
                href = parent_a.get("href")

                if not href:
                    continue

                if(not href.endswith(".pdf")):
                    continue

                vacancy_links.append((opening_header, href))

        if not vacancy_links:
            print("No vacancy links found")
            return

        for opening_header, pdf_link in vacancy_links:
            try:
                if pdf_link.startswith("http://"):
                    pdf_link = "https://" + pdf_link[len("http://"):]

                if is_url_saved(pdf_link):
                    print(f"Already saved in DB: {pdf_link}")
                    continue

                save_job_opening(
                    government_body="ICMR",
                    job_title=opening_header,
                    job_tag=None,
                    posted_date=None,
                    deadline=None,
                    url=pdf_link,
                )

                print (f"Saved to DB: {opening_header}")
                saved_count += 1

            except Exception as ex:
                print(f"Failed downloading: {pdf_link}")
                print(ex)

        browser.close()

    print(f"ICMR scraper saved {saved_count} records")


if __name__ == "__main__":
    scrape()