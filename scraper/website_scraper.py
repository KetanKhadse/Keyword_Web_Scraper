import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d[\d\s\-\(\)]{8,}\d)"

CONNECT_TIMEOUT = 3
READ_TIMEOUT = 5
MAX_HTML_SIZE = 1_000_000   # 🔥 smaller = faster


def scrape_company(url):
    domain = urlparse(url).netloc

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
            allow_redirects=True
        )

        # 🚫 Skip non-HTML
        content_type = r.headers.get("Content-Type", "").lower()
        if "text/html" not in content_type:
            raise ValueError("Non-HTML content")

        html = r.text[:MAX_HTML_SIZE]
        soup = BeautifulSoup(html, "html.parser")

        title = (
            soup.title.text.strip()
            if soup.title and soup.title.text
            else domain
        )

        # ✅ Extract only meaningful text
        texts = []

        for tag in soup.find_all(["p", "a", "li", "span"]):
            t = tag.get_text(" ", strip=True)
            if t:
                texts.append(t)

        visible_text = " ".join(texts)[:5000]

        emails = set(re.findall(EMAIL_REGEX, visible_text))
        phones = set(re.findall(PHONE_REGEX, visible_text))

        return {
            "company_name": title,
            "website": url,
            "email": ", ".join(emails),
            "phone": ", ".join(phones),
            "about_text": visible_text[:3000],
            "footer_text": "",
            "raw_text": visible_text.lower()
        }

    except Exception as e:
        # ❗ FAST FAIL — do NOT block pipeline
        return {
            "company_name": domain,
            "website": url,
            "email": "",
            "phone": "",
            "about_text": "",
            "footer_text": "",
            "raw_text": ""
        }



#================Last Working Start ===========================




# import requests
# import re
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse

# HEADERS = {
#     "User-Agent": "Mozilla/5.0",
#     "Accept": "text/html"
# }

# EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# PHONE_REGEX = r"(\+?\d[\d\s\-\(\)]{8,}\d)"

# # ⛔ HARD limits
# CONNECT_TIMEOUT = 3
# READ_TIMEOUT = 5
# MAX_HTML_SIZE = 2_000_000  # 2MB


# def scrape_company(url):
#     try:
#         session = requests.Session()
#         session.headers.update(HEADERS)

#         r = session.get(
#             url,
#             timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
#             allow_redirects=True,
#             stream=True
#         )

#         content = r.raw.read(MAX_HTML_SIZE, decode_content=True)
#         soup = BeautifulSoup(content, "html.parser")

#         title = soup.title.text.strip() if soup.title else urlparse(url).netloc
#         text = soup.get_text(" ", strip=True)

#         emails = set(re.findall(EMAIL_REGEX, text))
#         phones = set(re.findall(PHONE_REGEX, text))

#         linkedin = ""
#         for a in soup.find_all("a", href=True):
#             if "linkedin.com/company" in a["href"]:
#                 linkedin = a["href"]
#                 break

#         return {
#             "company_name": title,
#             "website": url,
#             "email": ", ".join(emails),
#             "phone": ", ".join(phones),
#             "linkedin": linkedin
#             # "about_text": text[:3000],  # prevent bloat
#             # "footer_text": ""
#         }

#     except Exception as e:
#         return {
#             "company_name": urlparse(url).netloc,
#             "website": url,
#             "email": "",
#             "phone": "",
#             "linkedin": ""
#             # "about_text": "",
#             # "footer_text": ""
#         }

#================Last Working End ===========================





# import requests
# import re
# from bs4 import BeautifulSoup
# from urllib.parse import urlparse, urljoin

# HEADERS = {"User-Agent": "Mozilla/5.0"}
# EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# PHONE_REGEX = r"(\+?\d[\d\s\-\(\)]{8,}\d)"

# CONTACT_KEYWORDS = ["contact", "about", "imprint", "legal"]
# TIMEOUT = 5


# def scrape_company(url):
#     try:
#         r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
#         r.raise_for_status()

#         soup = BeautifulSoup(r.text, "html.parser")
#         name = soup.title.text.strip() if soup.title else urlparse(url).netloc
#         text = soup.get_text(" ", strip=True)

#         emails = set(re.findall(EMAIL_REGEX, text))
#         phones = set(re.findall(PHONE_REGEX, text))

#         linkedin = ""
#         for a in soup.find_all("a", href=True):
#             if "linkedin.com/company" in a["href"]:
#                 linkedin = a["href"]
#                 break

#         return {
#             "company_name": name,
#             "website": url,
#             "email": ", ".join(emails),
#             "phone": ", ".join(phones),
#             "linkedin": linkedin,
#             "raw_text": text.lower()
#         }

#     except Exception:
#         return {
#             "company_name": urlparse(url).netloc,
#             "website": url,
#             "email": "",
#             "phone": "",
#             "linkedin": "",
#             "raw_text": ""
#         }


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
