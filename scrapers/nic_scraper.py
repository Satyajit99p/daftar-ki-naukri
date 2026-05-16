from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from common.data_service import is_url_saved, save_job_opening

BASE_URL = "https://recruitment.nic.in"


def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page_url = f"{BASE_URL}/index_new.php"
        print(f"Opening NIC vacancies page ")
        page.goto(page_url, wait_until="networkidle", timeout=120000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)
        vacancy_links = []

        for link in links:
            opening_header = link.get_text(strip=True).lower()

            href = link.get("href")

            if not href:
                continue

            if(not href.endswith(".pdf")):
                continue

            full_url = f"{BASE_URL}/{href}"

            vacancy_links.append((opening_header, full_url))

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
                    government_body="NIC",
                    job_title=opening_header,
                    job_tag=None,
                    posted_date=None,
                    deadline=None,
                    url=pdf_link,
                )

                print (f"Saved to DB: {opening_header}")

            except Exception as ex:
                print(f"Failed downloading: {pdf_link}")
                print(ex)

        browser.close()


if __name__ == "__main__":
    scrape()