from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from common.data_service import is_url_saved, save_job_opening

BASE_URL = "https://www.iitbbs.ac.in/index.php/home/jobs/non-teaching-jobs"

def scrape_page(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Get ONLY the first jobs section (currently open)
    first_widget = soup.select_one("div.elementor-widget-posts")

    if not first_widget:
        return [], None

    valid_data = []

    articles = first_widget.select("article.elementor-post")

    for article in articles:
        title_tag = article.select_one(".elementor-post__title a")
        date_tag = article.select_one(".elementor-post-date")

        if not title_tag:
            continue

        title = title_tag.get_text(" ", strip=True)
        href = title_tag.get("href", "").strip()

        if href:
            href = urljoin(url, href)

        posted_date = (
            date_tag.get_text(" ", strip=True)
            if date_tag else None
        )

        valid_data.append({
            "title": title,
            "url": href,
            "date": posted_date
        })

    return valid_data

def scrape():
    saved_count = 0
    page_number = 1

    while True:
        page_url = (
            BASE_URL
            if page_number == 1
            else f"{BASE_URL}/{page_number}/"
        )
        print(f"Scraping page: {page_url}")
        try:
            job_openings = scrape_page(page_url)

            if not job_openings:
                break

            for opening in job_openings:
                url = opening["url"]

                if not url:
                    continue

                if is_url_saved(url):
                    print(f"Already saved in DB: {url}")
                    continue

                save_job_opening(
                    government_body="IIT Bhubaneswar",
                    job_title=opening["title"],
                    job_tag=None,
                    posted_date=opening["date"],
                    deadline=None,
                    url=url,
                )
                saved_count += 1

        except Exception as e:
            print(f"Error scraping {page_url}: {e}")
            break

        page_number += 1

    print(f"Total new job openings saved: {saved_count}")

if __name__ == "__main__":
    scrape()