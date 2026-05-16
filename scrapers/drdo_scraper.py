from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from common.data_service import is_url_saved, save_job_opening

BASE_URL = "https://drdo.gov.in/drdo/en/offerings/vacancies"

def scrape():
    saved_count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()
        page_index = 0

        while True:

            page_url = f"{BASE_URL}?page={page_index}"
            print(f"Opening DRDO vacancies page {page_index}...")
            page.goto(page_url, wait_until="networkidle", timeout=120000)
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a")
            vacancy_links = []

            for link in links:
                href = link.get("href")

                if not href:
                    continue

                if(not href.startswith("http://drdo.gov.in/drdo/en/offerings/vacancies/")):
                    continue

                full_url = urljoin(BASE_URL, href)
                vacancy_links.append((link, full_url))

            if not vacancy_links:
                break

            for link, full_url in vacancy_links:
                print(f"Opening: {full_url}")
                opening_header = full_url.split("/")[-1]

                try:
                    page.goto(full_url, wait_until="networkidle", timeout=120000)
                    detail_html = page.content()
                    detail_soup = BeautifulSoup(detail_html, "html.parser")
                    pdf_links = []
                    potential_pdf_links = detail_soup.find_all("a")

                    for detail_anchor in potential_pdf_links:
                        detail_href = detail_anchor.get("href")

                        if not detail_href:
                            continue

                        detail_url = urljoin(full_url, detail_href)

                        if ".pdf" in detail_url.lower():
                            pdf_links.append(detail_url)

                    if not pdf_links:
                        print(f"No PDF link found on: {full_url}")
                        continue

                    if len(pdf_links) > 1:
                        pdf_link = full_url
                    else:
                        pdf_link = pdf_links[0]

                    if pdf_link.startswith("http://"):
                        pdf_link = "https://" + pdf_link[len("http://"):]

                    if is_url_saved(pdf_link):
                        print(f"Already saved in DB: {pdf_link}")
                        continue

                    save_job_opening(
                        government_body="DRDO",
                        job_title=opening_header,
                        job_tag=None,
                        posted_date=None,
                        deadline=None,
                        url=pdf_link,
                    )

                    print (f"Saved to DB: {opening_header}")
                    saved_count += 1

                except Exception as ex:
                    print(f"Failed downloading: {full_url}")
                    print(ex)

            page_index += 1
        browser.close()

    print(f"DRDO scraper saved {saved_count} records")


if __name__ == "__main__":
    scrape()