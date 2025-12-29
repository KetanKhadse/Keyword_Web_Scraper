import requests
from bs4 import BeautifulSoup


def find_linkedin(company_name, website):
    try:
        response = requests.get(website, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            if "linkedin.com/company" in a["href"]:
                return a["href"]

    except Exception:
        pass

    return ""
