import requests
from bs4 import BeautifulSoup
import re

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r'(\+?\d[\d\s\-\(\)]{7,}\d)'

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def scrape_company(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
         #Company Name
        title = soup.title.text.strip() if soup.title else "Unknown Company"

        #Email
        emails = set(re.findall(EMAIL_REGEX, response.text))

        # Contact
        phones = set()
        text = soup.get_text(separator=" ")
        for match in re.findall(PHONE_REGEX, text):
            phone = "".join(match).strip()
            if len(phone)>= 8:
                phones.add(phone)

        return {
            "company_name": title,
            "website": url,
            "email": ", ".join(emails) if emails else "",
            "phone": ", ".join(phones) if phones else ""
        }

    except Exception:
        return None
