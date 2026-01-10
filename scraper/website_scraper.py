import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

HEADERS = {"User-Agent": "Mozilla/5.0"}
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d[\d\s\-\(\)]{8,}\d)"

CONTACT_KEYWORDS = ["contact", "about", "imprint", "legal"]
TIMEOUT = 5


def scrape_company(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        name = soup.title.text.strip() if soup.title else urlparse(url).netloc
        text = soup.get_text(" ", strip=True)

        emails = set(re.findall(EMAIL_REGEX, text))
        phones = set(re.findall(PHONE_REGEX, text))

        linkedin = ""
        for a in soup.find_all("a", href=True):
            if "linkedin.com/company" in a["href"]:
                linkedin = a["href"]
                break

        return {
            "company_name": name,
            "website": url,
            "email": ", ".join(emails),
            "phone": ", ".join(phones),
            "linkedin": linkedin,
            "raw_text": text.lower()
        }

    except Exception:
        return {
            "company_name": urlparse(url).netloc,
            "website": url,
            "email": "",
            "phone": "",
            "linkedin": "",
            "raw_text": ""
        }


# import requests
# from bs4 import BeautifulSoup
# import re

# EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# PHONE_REGEX = r'(\+?\d[\d\s\-\(\)]{7,}\d)'

# HEADERS = {
#     "User-Agent": "Mozilla/5.0"
# }

# def find_contact_page(soup, base_url):
#     keywords = ["contact", "about", "reach", "connect", "imprint"]

#     for a in soup.find_all("a", href=True):
#         href = a["href"].lower()
#         text = a.get_text().lower()

#         if any(k in href or k in text for k in keywords):
#             if href.startswith("http"):
#                 return href
#             elif href.startswith("/"):
#                 return base_url.rstrip("/") + href

#     return None

# def scrape_company(url):
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")

#         title = soup.title.text.strip() if soup.title else "Unknown Company"

#         text = soup.get_text(separator=" ")

#         emails = set(re.findall(EMAIL_REGEX, text))
#         phones = set(re.findall(PHONE_REGEX, text))

#         linkedin = ""
#         for a in soup.find_all("a", href=True):
#             if "linkedin.com/company" in a["href"]:
#                 linkedin = a["href"]
#                 break

#         # 🔁 FOLLOW CONTACT PAGE IF DATA IS MISSING
#         if not emails or not phones:
#             contact_url = find_contact_page(soup, url)

#             if contact_url:
#                 print("➡️ Following contact page:", contact_url)
#                 try:
#                     c_resp = requests.get(contact_url, headers=HEADERS, timeout=10)
#                     c_soup = BeautifulSoup(c_resp.text, "html.parser")
#                     c_text = c_soup.get_text(separator=" ")

#                     emails.update(re.findall(EMAIL_REGEX, c_text))
#                     phones.update(re.findall(PHONE_REGEX, c_text))

#                 except Exception:
#                     pass

#         return {
#             "company_name": title,
#             "website": url,
#             "email": ", ".join(emails) if emails else "",
#             "phone": ", ".join(phones) if phones else "",
#             "linkedin": linkedin
#         }

#     except Exception as e:
#         print("Scrape failed:", e)
#         return None
