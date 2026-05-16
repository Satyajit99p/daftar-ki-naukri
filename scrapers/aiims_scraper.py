from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from common.data_service import is_url_saved, save_job_opening

BASE_URL_AIIMS_BBSR = "https://aiimsbhubaneswar.nic.in/recruitment-notice/"
BASE_URL_AIIMS_MANGALGIRI = "https://www.aiimsmangalagiri.edu.in/vacancies/"
BASE_URL_AIIMS_Delhi = "https://www.aiims.edu/index.php/en/notices/recruitment/aiims-recruitment"


def _normalize_pdf_url(base_url, href):
    full_url = urljoin(base_url, href)

    if full_url.startswith("http://"):
        full_url = "https://" + full_url[len("http://"):]

    return full_url


def _extract_pdf_links(html, base_url):
    # Generic PDF extraction for AIIMS pages that expose files via anchor tags.
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    results = []

    for link in links:
        href = link.get("href", "")

        if ".pdf" not in href.lower():
            continue

        title = link.get_text(strip=True) or link.get("aria-label", "").strip()

        if not title:
            title = href.split("/")[-1]

        results.append((title, _normalize_pdf_url(base_url, href)))

    return results


def _save_openings(government_body, items):
    saved_count = 0
    for opening_header, pdf_link in items:
        if is_url_saved(pdf_link):
            print(f"Already saved in DB: {pdf_link}")
            continue

        save_job_opening(
            government_body=government_body,
            job_title=opening_header,
            job_tag=None,
            posted_date=None,
            deadline=None,
            url=pdf_link,
        )

        print(f"Saved to DB: {opening_header}")
        saved_count += 1

    print(f"{government_body} scraper saved {saved_count} records")
    return saved_count

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        bbsr_links = parse_aiims_bbsr(browser, BASE_URL_AIIMS_BBSR)
        mangalagiri_links = parse_aiims_mangalagiri(browser, BASE_URL_AIIMS_MANGALGIRI)
        delhi_links = parse_aiims_delhi(browser, BASE_URL_AIIMS_Delhi)

        _save_openings("AIIMS BBSR", bbsr_links)
        _save_openings("AIIMS Mangalagiri", mangalagiri_links)
        _save_openings("AIIMS Delhi", delhi_links)

        browser.close()

def parse_aiims_bbsr(browser, url):
    page = browser.new_page()
    print(f"Opening AIIMS BBSR vacancies page ")
    page.goto(url, wait_until="networkidle", timeout=120000)
    html = page.content()
    results = _extract_pdf_links(html, url)
    page.close()
    return results


def parse_aiims_mangalagiri(browser, url):
    page = browser.new_page()
    print("Opening AIIMS Mangalagiri vacancies page")
    page.goto(url, wait_until="networkidle", timeout=120000)
    html = page.content()
    results = _extract_pdf_links(html, url)
    page.close()
    return results


def parse_aiims_delhi(browser, url):
    page = browser.new_page()
    print("Opening AIIMS Delhi vacancies page")
    page.goto(url, wait_until="networkidle", timeout=120000)
    html = page.content()
    results = _extract_pdf_links(html, url)
    page.close()
    return results

if __name__ == "__main__":
    scrape()