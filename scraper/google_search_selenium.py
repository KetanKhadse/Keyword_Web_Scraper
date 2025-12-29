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
    # Keep this OFF for demo
    # options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    collected_urls = set()

    for ctype in company_types:
        query = f"{product} {ctype} {country}"
        print("Google search query:", query)

        driver.get(f"https://www.google.com/search?q={query}")
        time.sleep(5)

        links = driver.find_elements(By.CSS_SELECTOR, "a")

        for link in links:
            href = link.get_attribute("href")

            if (
                href
                and href.startswith("http")
                and "google" not in href
                and "youtube" not in href
            ):
                collected_urls.add(href)

            if len(collected_urls) >= limit:
                break

        if len(collected_urls) >= limit:
            break

    driver.quit()

    print(f"Collected {len(collected_urls)} URLs")
    return list(collected_urls)
