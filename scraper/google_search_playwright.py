# scraper/google_search_playwright.py
import time
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

def extract_google_url(href: str):
    if "/url?" not in href:
        return href
    parsed = urlparse(href)
    qs = parse_qs(parsed.query)
    return qs.get("q", [None])[0]

def search_companies(product, country, company_types):
    collected = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(locale="en-US")
        page = context.new_page()

        for ctype in company_types:
            query = f"{product} {ctype} in {country}"
            for page_no in range(0, 10):
                start = page_no * 10
                url = f"https://www.google.com/search?q={query}&hl=en&num=10&start={start}"
                print(f"🔎 Google: {query} | Page {page_no + 1}")
                page.goto(url)
                time.sleep(3)

                # Extract links
                links = page.locator("a").all()
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue
                    real = extract_google_url(href)
                    if not real:
                        continue
                    parsed = urlparse(real)
                    if parsed.scheme.startswith("http") and parsed.netloc:
                        collected.add(real)

        context.close()
        browser.close()

    return list(collected)
