import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def search_companies(product, country, company_types, limit):
    results = set()

    for ctype in company_types:
        query = f"{product} {country} company"
        url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"

        print("Searching:", query)

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            links = soup.select("a.result__a")

            print(f"Found {len(links)} search results")

            for link in links:
                href = link.get("href")
                if href and href.startswith("http"):
                    results.add(href)

                if len(results) >= limit:
                    break

        except Exception as e:
            print("Search error:", e)

        time.sleep(2)

    return list(results)
