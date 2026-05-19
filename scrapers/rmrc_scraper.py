from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from common.data_service import is_url_saved, save_job_opening
from common.utils import parse_timestamp

BASE_URL = "https://www.rmrcbbsr.gov.in/career/"

def scrape():
    saved_count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page_url = f"{BASE_URL}"
        print(f"Opening RMRC vacancies page ")
        page.goto(page_url, wait_until="networkidle", timeout=120000)
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        vacancy_links = []

        # Find the first h2 (Advertisement Details)
        first_h2 = soup.find("h2", string=lambda x: x and "Advertisement Details" in x)

        if not first_h2:
            print("Advertisement section not found")
            return

        # Get the next div with class 'inner' (this is the correct container)
        inner_div = first_h2.find_next("div", class_="inner")

        if not inner_div:
            print("Inner div not found")
            return

        # Now scope table extraction ONLY inside this div
        rows = inner_div.select("table tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            post = cols[2].get_text(strip=True)
            last_date = cols[4].get_text(strip=True)
            posted_date = cols[3].get_text(strip=True)

            posted_date = parse_timestamp(posted_date)
            last_date = parse_timestamp(last_date)

            view_url = cols[5].find("a", href=True).get("href")
            
            vacancy_links.append({
                "post": post,
                "last_date": last_date,
                "posted_date": posted_date,
                "url": view_url
            })

        if not vacancy_links:
            print("No vacancy links found")
            return

        for link_data in vacancy_links:
            opening_header = link_data["post"]
            pdf_link = link_data["url"]
            try:
                if pdf_link.startswith("http://"):
                    pdf_link = "https://" + pdf_link[len("http://"):]

                if is_url_saved(pdf_link):
                    print(f"Already saved in DB: {pdf_link}")
                    continue

                save_job_opening(
                    government_body="RMRC",
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