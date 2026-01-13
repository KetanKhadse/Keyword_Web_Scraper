# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import StaleElementReferenceException
# from urllib.parse import quote_plus, urlparse
# import time


# def search_companies(product, country, company_types, max_results):
#     """
#     Brave Search scraper
#     - Uses Brave browser
#     - Uses Brave Search engine
#     - Returns clean company URLs
#     """

#     options = Options()

#     # ✅ USE BRAVE BROWSER
#     options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

#     # 🔒 Anti-detection (safe)
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--start-maximized")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     # ❌ Do NOT use headless
#     driver = webdriver.Chrome(options=options)

#     collected = set()

#     try:
#         for ctype in company_types:
#             query = f"{product} {ctype} {country}"

#             # Brave Search pagination uses page=1,2,3...
#             for page in range(1, 11):  # ~100 results max
#                 if len(collected) >= max_results:
#                     break

#                 url = (
#                     "https://search.brave.com/search?"
#                     f"q={quote_plus(query)}&page={page}"
#                 )

#                 print(f"🦁 Brave Search: {query} | Page {page}")
#                 driver.get(url)

#                 # ⏳ Give time for page + manual intervention if needed
#                 time.sleep(5)

#                 try:
#                     results = driver.find_elements(
#                         By.XPATH,
#                         "//a[@data-testid='result-title-a']"
#                     )
#                 except Exception:
#                     continue

#                 for a in results:
#                     if len(collected) >= max_results:
#                         break

#                     try:
#                         href = a.get_attribute("href")
#                     except StaleElementReferenceException:
#                         continue

#                     if not href:
#                         continue

#                     parsed = urlparse(href)
#                     if parsed.scheme.startswith("http") and parsed.netloc:
#                         collected.add(href)

#     finally:
#         driver.quit()

#     return list(collected)


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import quote_plus, urlparse, parse_qs
import time


def extract_google_url(href):
    # handles /url?q=realurl&sa=...
    if "/url?" in href:
        qs = parse_qs(urlparse(href).query)
        if "q" in qs:
            return qs["q"][0]
    return href



def search_companies(product, country, company_types, max_results):
    options = Options()

    #🔥 anti-detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    # ✅ USE YOUR LOGGED-IN CHROME PROFILE
    # options.add_argument(
    #     r"--user-data-dir=C:\Users\Hp\AppData\Local\Google\Chrome\User Data\Default"
    # )
    # options.add_argument("--profile-directory=Default")

    # # 🔒 Anti-detection (safe)
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--start-maximized")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    # # ❗ DO NOT USE headless for Google
    driver = webdriver.Chrome(options=options)
    collected = set()
    

    try:
        for ctype in company_types:
            query = f"{product} {ctype} in {country}"

            for page in range(0,15):
                url = (
                    "https://www.google.com/search?"
                    f"q={quote_plus(query)}&hl=en&gl=de&num=10&start={page*10}"
                )

                print(f"🔎 Google: {query} | Page {page + 1}")
                driver.get(url)
                time.sleep(20)

                # ✅ Handle consent (EU)
                try:
                    agree = driver.find_element(By.XPATH, "//button//*[text()='I agree']")
                    agree.click()
                    time.sleep(2)
                except Exception:
                    pass

                anchors = driver.find_elements(By.XPATH, "//a[@href]")
                for a in anchors:
                    href = a.get_attribute("href")
                    if not href:
                        continue

                    if "/url?" in href or href.startswith("http"):
                        real = extract_google_url(href)

                        parsed = urlparse(real)
                        if parsed.scheme.startswith("http") and parsed.netloc:
                            collected.add(real)

                if len(collected) >= max_results:
                    break

    finally:
        driver.quit()

    return list(collected)






# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import urllib.parse


# def search_companies(product, country, company_types, limit=20, max_pages=10):
#     """
#     Google search scraper (STALE-SAFE)
#     Returns unique result URLs
#     """

#     options = Options()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--start-maximized")

#     driver = webdriver.Chrome(options=options)
#     wait = WebDriverWait(driver, 10)

#     collected_urls = set()

#     try:
#         for company_type in company_types:
#             page = 0

#             while len(collected_urls) < limit and page < max_pages:
#                 query = f"{product} {company_type} {country}"
#                 encoded_query = urllib.parse.quote_plus(query)

#                 start = page * 10
#                 search_url = f"https://www.google.com/search?q={encoded_query}&start={start}"

#                 print(f"Google search query: {query} | Page {page + 1}")
#                 driver.get(search_url)

#                 time.sleep(2)

#                 # Wait for search results container
#                 wait.until(EC.presence_of_element_located((By.ID, "search")))

#                 # 🔑 CRITICAL FIX:
#                 # Extract hrefs directly from DOM (not WebElement reuse)
#                 links = driver.find_elements(By.XPATH, "//div[@id='search']//a[@href]")

#                 new_urls = 0

#                 for link in links:
#                     try:
#                         href = link.get_attribute("href")
#                     except:
#                         continue

#                     if not href:
#                         continue

#                     # Filter garbage
#                     if any(x in href for x in [
#                         "google.com",
#                         "/search?",
#                         "/preferences?",
#                         "policies.google.com",
#                         "support.google.com"
#                     ]):
#                         continue

#                     if href not in collected_urls:
#                         collected_urls.add(href)
#                         new_urls += 1

#                         if len(collected_urls) >= limit:
#                             break

#                 print(f"New URLs found on page {page + 1}: {new_urls}")

#                 if new_urls == 0:
#                     break

#                 page += 1
#                 time.sleep(1)

#     finally:
#         driver.quit()

#     return list(collected_urls)
