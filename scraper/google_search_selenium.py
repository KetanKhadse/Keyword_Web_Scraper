import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def search_companies(product, country, company_types, limit):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    # Keep headless OFF for demo
    # options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    collected_urls = set()
    results_per_page = 10
    max_pages = 10  # safety cap (can increase later)

    for ctype in company_types:
        page = 0

        while len(collected_urls) < limit and page < max_pages:
            start = page * results_per_page
            query = f"{product} {ctype} {country}"

            search_url = f"https://www.google.com/search?q={query}&start={start}"
            print(f"Google search query: {query} | Page {page + 1}")

            driver.get(search_url)
            time.sleep(4)

            links = driver.find_elements(By.CSS_SELECTOR, "a")
            new_links_found = 0

            for link in links:
                href = link.get_attribute("href")

                if (
                    href
                    and href.startswith("http")
                    and "google." not in href
                    and "youtube.com" not in href
                ):
                    if href not in collected_urls:
                        collected_urls.add(href)
                        new_links_found += 1

                if len(collected_urls) >= limit:
                    break

            print(f"New URLs found on page {page + 1}: {new_links_found}")

            # If no new links were found, stop paginating
            if new_links_found == 0:
                print("No new results, stopping pagination for this query.")
                break

            page += 1

    driver.quit()

    print(f"Collected {len(collected_urls)} URLs")
    return list(collected_urls)
