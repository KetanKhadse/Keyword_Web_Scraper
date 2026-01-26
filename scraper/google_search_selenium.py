from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from headers import get_random_user_agent
#from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import quote_plus, urlparse, parse_qs
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException


def extract_google_url(href):
    # handles /url?q=realurl&sa=...
    if "/url?" in href:
        qs = parse_qs(urlparse(href).query)
        if "q" in qs:
            return qs["q"][0]
    return href


user_Header = get_random_user_agent()
def search_companies(product, country, company_types, max_results):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={user_Header}")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    collected = set()

    try:
        for ctype in company_types:
            query = f"{product} {ctype} in {country}"

            for page in range(0, 10):
                if len(collected) >= max_results:
                    break

                url = (
                    "https://www.google.com/search?"
                    f"q={quote_plus(query)}&hl=en&gl=de&num=10&start={page * 10}"
                )

                print(f"🔎 Google: {query} | Page {page + 1}")
                driver.get(url)
                time.sleep(20)

                # Handle EU consent (safe)
                try:
                    agree = wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button//*[text()='I agree']")
                        )
                    )
                    agree.click()
                    time.sleep(1)
                except TimeoutException:
                    pass

                try:
                    # Wait until results exist
                    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@href]")))
                except TimeoutException:
                    continue

                # 🔑 CRITICAL FIX: extract hrefs immediately
                anchors = driver.find_elements(By.XPATH, "//a[@href]")
                for a in anchors:
                    try:
                        href = a.get_attribute("href")
                    except StaleElementReferenceException:
                        continue

                    if not href:
                        continue

                    if "/url?" in href or href.startswith("http"):
                        real = extract_google_url(href)
                        parsed = urlparse(real)

                        if parsed.scheme.startswith("http") and parsed.netloc:
                            collected.add(real)

                    if len(collected) >= max_results:
                        break

                time.sleep(1.5)

    finally:
        driver.quit()

    return list(collected)