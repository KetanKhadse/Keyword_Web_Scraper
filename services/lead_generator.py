from urllib.parse import urlparse
import time
import re

from scraper.google_search_selenium import search_companies
from scraper.website_scraper import scrape_company
from scraper.linkedin_finder import find_linkedin
from services.excel_service import generate_excel
from config.regions import REGIONS

# ---------------- CONFIG ---------------- #

BAD_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip"
)

DELAY_BETWEEN_QUERIES = 1.5

# ❌ Countries to EXCLUDE
CHINA_KEYWORDS = [
    "china", "prc", "made in china", "shanghai",
    "shenzhen", "beijing", "guangzhou"
]

INDIA_KEYWORDS = [
    "india", "bharat", "made in india",
    "mumbai", "bangalore", "chennai",
    "hyderabad", "pune"
]

CHINA_TLDS = (".cn", ".com.cn")
INDIA_TLDS = (".in", ".co.in")

CHINA_PHONE = re.compile(r"\+?86")
INDIA_PHONE = re.compile(r"\+?91")

# ---------------- HELPERS ---------------- #

def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc:
        return False
    if any(url.lower().endswith(ext) for ext in BAD_EXTENSIONS):
        return False
    return True


def split_product_terms(product_string: str) -> list[str]:
    return [p.strip() for p in product_string.split(",") if p.strip()]


def resolve_countries(country: str | None, region: str | None) -> list[str]:
    if region and region in REGIONS:
        return REGIONS[region]
    if country:
        return [country]
    return []


def detect_keywords(text: str, keywords: list[str]) -> bool:
    if not text:
        return False
    text = text.lower()
    return any(k in text for k in keywords)


# 🔥 STRICT COUNTRY VALIDATION
def is_valid_for_selected_country(data: dict, domain: str, country: str) -> bool:
    """
    ACCEPT ONLY if company clearly belongs to selected country
    """

    country = country.lower()

    combined_text = " ".join([
        data.get("company_name", ""),
        data.get("about_text", ""),
        data.get("footer_text", ""),
        data.get("raw_text", ""),
    ]).lower()

    phone = data.get("phone", "")

    # 🚫 HARD EXCLUSIONS (China / India)
    if detect_keywords(combined_text, CHINA_KEYWORDS):
        return False
    if detect_keywords(combined_text, INDIA_KEYWORDS):
        return False
    if domain.endswith(CHINA_TLDS) or domain.endswith(INDIA_TLDS):
        return False
    if CHINA_PHONE.search(phone) or INDIA_PHONE.search(phone):
        return False

    # ✅ POSITIVE country signals (REQUIRED)
    positive_signals = 0

    # Country name
    if country in combined_text:
        positive_signals += 1

    # ccTLD
    if domain.endswith(f".{country[:2]}"):
        positive_signals += 1

    # Phone country code (basic map)
    COUNTRY_PHONE_CODES = {
        "israel": "+972",
        "germany": "+49",
        "france": "+33",
        "italy": "+39",
        "spain": "+34",
        "uk": "+44",
        "united states": "+1",
        "usa": "+1",   
    "netherlands": "+31",
    "belgium": "+32",
    "switzerland": "+41",
    "austria": "+43",
    "sweden": "+46",
    "norway": "+47",
    "finland": "+358",
    "poland": "+48"
    }

    code = COUNTRY_PHONE_CODES.get(country)
    if code and code in phone:
        positive_signals += 1

    # ❌ If country not clearly proven — reject
    return positive_signals > 0


# ---------------- MAIN ---------------- #

def generate_leads(product, country, company_types, limit, region=None):
    print("=== Lead generation started ===")
    print("STRICT country mode:", country)
    print("Limit:", limit)

    product_terms = split_product_terms(product)
    countries = resolve_countries(country, region)

    leads = []
    seen_domains = set()

    for c in countries:
        print(f"\n🌍 Country LOCKED: {c}")
        collected_for_country = 0

        for term in product_terms:
            for ctype in company_types:
                if collected_for_country >= limit:
                    break

                urls = search_companies(
                    product=term,
                    country=c,
                    company_types=[ctype],
                    max_results=limit * 5
                )

                for url in urls:
                    if collected_for_country >= limit:
                        break

                    if not is_valid_url(url):
                        continue

                    domain = urlparse(url).netloc.lower().replace("www.", "")

                    if domain in seen_domains:
                        continue

                    print(f"🔧 Scraping: {domain}")
                    data = scrape_company(url)

                    if not is_valid_for_selected_country(data, domain, c):
                        print(f"🚫 Rejected (not strictly {c}): {domain}")
                        seen_domains.add(domain)
                        continue

                    data["linkedin"] = find_linkedin(
                        company_name=data.get("company_name"),
                        website=url
                    )

                    data["products"] = term
                    data["country"] = c
                    data["domain"] = domain

                    leads.append(data)
                    seen_domains.add(domain)
                    collected_for_country += 1

                    print(
                        f"✅ Added ({collected_for_country}/{limit}): "
                        f"{data.get('company_name')}"
                    )

                time.sleep(DELAY_BETWEEN_QUERIES)

        print(f"✔ STRICTLY collected {collected_for_country} companies for {c}")

    print(f"\n✅ Total leads collected: {len(leads)}")

    excel_path = generate_excel(leads)
    return leads, excel_path


# from urllib.parse import urlparse
# import time

# from scraper.google_search_selenium import search_companies
# from scraper.website_scraper import scrape_company
# from scraper.linkedin_finder import find_linkedin
# from services.excel_service import generate_excel
# from config.regions import REGIONS

# # ---------------- CONFIG ---------------- #

# BAD_EXTENSIONS = (
#     ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip"
# )

# DELAY_BETWEEN_QUERIES = 1.5

# CHINA_KEYWORDS = [
#     "china",
#     "people's republic of china",
#     "prc",
#     "made in china",
#     "china office",
#     "china branch",
#     "chinese subsidiary",
#     "shanghai",
#     "shenzhen",
#     "beijing",
#     "guangzhou",
#     "zhejiang",
#     "guangdong"
# ]

# INDIA_KEYWORDS = [
#     "india",
#     "bharat",
#     "made in india",
#     "india office",
#     "india branch",
#     "indian subsidiary",
#     "new delhi",
#     "mumbai",
#     "bangalore",
#     "bengaluru",
#     "chennai",
#     "hyderabad",
#     "pune",
#     "ahmedabad"
# ]

# JUNK_DOMAINS = (
#     "google.",
#     "cnn.",
#     "signin",
#     "login",
#     "accounts.google",
#     "youtube.",
#     "facebook.",
#     "wikipedia.",
# )

# # -------------------------------------- #


# # ---------------- HELPERS ---------------- #

# def is_valid_url(url: str) -> bool:
#     """
#     ONLY filter:
#     - invalid URLs
#     - unwanted file formats
#     """
#     parsed = urlparse(url)

#     if not parsed.netloc:
#         return False

#     if any(url.lower().endswith(ext) for ext in BAD_EXTENSIONS):
#         return False

#     return True


# def split_product_terms(product_string: str) -> list[str]:
#     return [p.strip() for p in product_string.split(",") if p.strip()]


# def resolve_countries(country: str | None, region: str | None) -> list[str]:
#     if region and region in REGIONS:
#         return REGIONS[region]

#     if country:
#         return [country]

#     return []


# def detect_affiliation(text: str, keywords: list[str]) -> bool:
#     """
#     Generic country signal detector.
#     FLAG ONLY — no rejection.
#     """
#     if not text:
#         return False

#     text = text.lower()
#     return any(k in text for k in keywords)


# # ---------------- MAIN ---------------- #
# def generate_leads(product, country, company_types, limit, region=None):
#     print("=== Lead generation started ===")
#     print("Limit:", limit)

#     product_terms = split_product_terms(product)
#     countries = resolve_countries(country, region)

#     leads = []
#     seen_domains = set()

#     for c in countries:
#         print(f"\n🌍 Country: {c}")
#         collected_for_country = 0

#         for term in product_terms:
#             for ctype in company_types:
#                 if collected_for_country >= limit:
#                     break

#                 urls = search_companies(
#                     product=term,
#                     country=c,
#                     company_types=[ctype],
#                     max_results=limit * 5
#                 )

#                 for url in urls:
#                     if collected_for_country >= limit:
#                         break

#                     if not is_valid_url(url):
#                         continue

#                     domain = urlparse(url).netloc.lower().replace("www.", "")

#                     if domain in seen_domains:
#                         continue

#                     if any(j in domain for j in JUNK_DOMAINS):
#                         continue

#                     print(f"🔧 Scraping: {domain}")

#                     data = scrape_company(url)

#                     combined_text = " ".join([
#                         data.get("company_name", ""),
#                         data.get("footer_text", ""),
#                         data.get("about_text", "")
#                     ])

#                     data["china_affiliation"] = detect_affiliation(
#                         combined_text, CHINA_KEYWORDS
#                     )

#                     data["india_affiliation"] = detect_affiliation(
#                         combined_text, INDIA_KEYWORDS
#                     )

#                     data["linkedin"] = find_linkedin(
#                         company_name=data.get("company_name"),
#                         website=url
#                     )

#                     data["products"] = term
#                     data["country"] = c
#                     data["domain"] = domain

#                     leads.append(data)
#                     seen_domains.add(domain)
#                     collected_for_country += 1

#                     print(f"✅ Added ({collected_for_country}/{limit}): {data.get('company_name')}")

#                 time.sleep(DELAY_BETWEEN_QUERIES)

#         print(f"✔ Collected {collected_for_country} companies for {c}")

#     print(f"\n✅ Total leads collected: {len(leads)}")

#     excel_leads = []
#     for lead in leads:
#         clean = lead.copy()
#         clean.pop("china_affiliation", None)
#         clean.pop("india_affiliation", None)
#         excel_leads.append(clean)

#     excel_path = generate_excel(excel_leads)
#     return leads, excel_path

# def generate_leads(
#     product: str,
#     country: str | None,
#     company_types: list[str],
#     limit: int,
#     region: str | None = None
# ):
#     print("=== Lead generation started ===")
#     print("Limit:", limit)

#     product_terms = split_product_terms(product)
#     countries = resolve_countries(country, region)

#     leads = []
#     seen_domains = set()

#     for c in countries:
#         print(f"\n🌍 Country: {c}")
#         collected_for_country = 0

#         for term in product_terms:
#             for ctype in company_types:
#                 if collected_for_country >= limit:
#                     break

#                 urls = search_companies(
#                     product=term,
#                     country=c,
#                     company_types=[ctype],
#                     max_results=limit * 5
#                 )

#                 for url in urls:
#                     if collected_for_country >= limit:
#                         break

#                     if not is_valid_url(url):
#                         continue

#                     domain = urlparse(url).netloc.lower().replace("www.", "")
#                     if domain in seen_domains:
#                         continue

#                     data = scrape_company(url)

#                     combined_text = " ".join([
#                         data.get("company_name", ""),
#                         data.get("footer_text", ""),
#                         data.get("about_text", "")
#                     ])

#                     # 🇨🇳 China signal (FLAG ONLY)
#                     data["china_affiliation"] = detect_affiliation(
#                         combined_text,
#                         CHINA_KEYWORDS
#                     )

#                     # 🇮🇳 India signal (FLAG ONLY)
#                     data["india_affiliation"] = detect_affiliation(
#                         combined_text,
#                         INDIA_KEYWORDS
#                     )

#                     data["linkedin"] = find_linkedin(
#                         company_name=data.get("company_name"),
#                         website=url
#                     )

#                     data["products"] = term
#                     data["country"] = c
#                     data["domain"] = domain

#                     leads.append(data)
#                     seen_domains.add(domain)
#                     collected_for_country += 1

#                     print(
#                         f"✅ Added ({collected_for_country}/{limit}): "
#                         f"{data.get('company_name')}"
#                     )

#                 time.sleep(DELAY_BETWEEN_QUERIES)

#         print(f"✔ Collected {collected_for_country} companies for {c}")

#     print(f"\n✅ Total leads collected: {len(leads)}")

#     # 🚫 Do NOT export flags to Excel
#     excel_leads = []
#     for lead in leads:
#         clean_lead = lead.copy()
#         clean_lead.pop("china_affiliation", None)
#         clean_lead.pop("india_affiliation", None)
#         excel_leads.append(clean_lead)

#     excel_path = generate_excel(excel_leads)

#     return leads, excel_path






# from urllib.parse import urlparse
# import time

# from scraper.google_search_selenium import search_companies
# from scraper.website_scraper import scrape_company
# from scraper.linkedin_finder import find_linkedin
# from services.excel_service import generate_excel
# from config.regions import REGIONS

# # ---------------- CONFIG ---------------- #

# BAD_EXTENSIONS = (
#     ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip"
# )
# # CAPTCHA_WAIT_SECONDS = 30 
# DELAY_BETWEEN_QUERIES = 1.5

# CHINA_FOOTER_KEYWORDS = [
#     "china",
#     "people's republic of china",
#     "prc",
#     "made in china",
#     "china office",
#     "china branch",
#     "chinese subsidiary",
#     "shanghai",
#     "shenzhen",
#     "beijing",
#     "guangzhou",
#     "zhejiang",
#     "guangdong"
# ]

# # -------------------------------------- #


# # ---------------- HELPERS ---------------- #

# def is_valid_url(url: str) -> bool:
#     parsed = urlparse(url)

#     if not parsed.netloc:
#         return False

#     if parsed.netloc.endswith(".cn"):
#         return False

#     if any(url.lower().endswith(ext) for ext in BAD_EXTENSIONS):
#         return False

#     return True


# def split_product_terms(product_string: str) -> list[str]:
#     return [p.strip() for p in product_string.split(",") if p.strip()]


# def resolve_countries(country: str | None, region: str | None) -> list[str]:
#     if region and region in REGIONS:
#         return REGIONS[region]

#     if country:
#         return [country]

#     return []


# def build_hq_keywords(country: str | None, region: str | None) -> list[str]:
#     """
#     Dynamically build HQ keywords from selected country / region.
#     NO hardcoding of regions.
#     """
#     keywords = [
#         "headquarters",
#         "head office",
#         "corporate office",
#         "registered office",
#         "hq"
#     ]

#     if country:
#         keywords.append(country.lower())

#     if region and region in REGIONS:
#         for c in REGIONS[region]:
#             keywords.append(c.lower())

#     return list(set(keywords))


# def is_china_affiliated_footer(footer_text: str, hq_keywords: list[str]) -> bool:
#     """
#     Reject company ONLY if:
#     - China keywords present in footer
#     - AND no HQ country/region keywords present
#     """
#     if not footer_text:
#         return False

#     footer_text = footer_text.lower()

#     has_china = any(k in footer_text for k in CHINA_FOOTER_KEYWORDS)
#     has_hq = any(k in footer_text for k in hq_keywords)

#     return has_china and not has_hq


# # ---------------- MAIN ---------------- #

# def generate_leads(
#     product: str,
#     country: str | None,
#     company_types: list[str],
#     limit: int,
#     region: str | None = None
# ):
#     print("=== Lead generation started ===")
#     print("Limit:", limit)

#     product_terms = split_product_terms(product)
#     countries = resolve_countries(country, region)

#     leads = []
#     seen_domains = set()

#     for c in countries:
#         print(f"\n🌍 Country: {c}")
#         collected_for_country = 0

#         hq_keywords = build_hq_keywords(country=c, region=region)

#         for term in product_terms:
#             for ctype in company_types:
#                 if collected_for_country >= limit:
#                     break

#                 urls = search_companies(
#                     product=term,
#                     country=c,
#                     company_types=[ctype],
#                     max_results=limit * 5
#                 )

#                  # 🟡 CAPTCHA MANUAL WINDOW (CORRECT PLACE)
#                 # print(
#                 #     f"\n⏳ Waiting {CAPTCHA_WAIT_SECONDS} seconds — "
#                 #     f"solve CAPTCHA in browser if shown..."
#                 # )
#                 # time.sleep(CAPTCHA_WAIT_SECONDS)

#                 for url in urls:
#                     if collected_for_country >= limit:
#                         break

#                     if not is_valid_url(url):
#                         continue

#                     domain = urlparse(url).netloc.lower().replace("www.", "")
#                     if domain in seen_domains:
#                         continue

#                     data = scrape_company(url)

#                     # ❌ Footer-based China affiliation rejection
#                     if is_china_affiliated_footer(
#                         data.get("footer_text", ""),
#                         hq_keywords
#                     ):
#                         print(f"❌ China-affiliated (footer): {data.get('company_name')}")
#                         continue

#                     data["linkedin"] = find_linkedin(
#                         company_name=data.get("company_name"),
#                         website=url
#                     )

#                     data["products"] = term
#                     data["country"] = c
#                     data["domain"] = domain

#                     leads.append(data)
#                     seen_domains.add(domain)
#                     collected_for_country += 1

#                     print(
#                         f"✅ Added ({collected_for_country}/{limit}): "
#                         f"{data.get('company_name')}"
#                     )

#                 time.sleep(DELAY_BETWEEN_QUERIES)

#         print(f"✔ Collected {collected_for_country} companies for {c}")

#     print(f"\n✅ Total leads collected: {len(leads)}")
#     excel_path = generate_excel(leads)

#     return leads, excel_path





# # from urllib.parse import urlparse
# # import time

# # from scraper.google_search_selenium import search_companies
# # from scraper.website_scraper import scrape_company
# # from scraper.linkedin_finder import find_linkedin
# # from services.excel_service import generate_excel
# # from config.regions import REGIONS

# # BAD_EXTENSIONS = (".pdf", ".doc", ".xls", ".zip")
# # DELAY = 1.2


# # def is_valid_url(url):
# #     parsed = urlparse(url)
# #     if not parsed.netloc:
# #         return False
# #     if parsed.netloc.endswith(".cn"):
# #         return False
# #     if any(url.lower().endswith(e) for e in BAD_EXTENSIONS):
# #         return False
# #     return True


# # def resolve_countries(country, region):
# #     if region and region in REGIONS:
# #         return REGIONS[region]
# #     if country:
# #         return [country]
# #     return []


# # def generate_leads(product, country, company_types, limit, region=None):
# #     product_terms = [p.strip() for p in product.split(",") if p.strip()]
# #     countries = resolve_countries(country, region)

# #     leads = []
# #     seen_domains = set()

# #     for c in countries:
# #         print(f"\n🌍 Country: {c}")
# #         count = 0

# #         for term in product_terms:
# #             for ctype in company_types:
# #                 if count >= limit:
# #                     break

# #                 urls = search_companies(
# #                     product=term,
# #                     country=c,
# #                     company_types=[ctype],
# #                     max_results=limit * 5
# #                 )

# #                 for url in urls:
# #                     if count >= limit:
# #                         break

# #                     if not is_valid_url(url):
# #                         continue

# #                     domain = urlparse(url).netloc.replace("www.", "")
# #                     if domain in seen_domains:
# #                         continue

# #                     data = scrape_company(url)

# #                     # 🇨🇳 Final China exclusion (content based)
# #                     if ".cn" in domain:
# #                         continue

# #                     data["linkedin"] = find_linkedin(
# #                         company_name=data["company_name"],
# #                         website=url
# #                     )

# #                     data["country"] = c
# #                     data["products"] = term
# #                     data["domain"] = domain

# #                     seen_domains.add(domain)
# #                     leads.append(data)
# #                     count += 1

# #                     print(f"✅ {count}/{limit}: {data['company_name']}")

# #                 time.sleep(DELAY)

# #         print(f"✔ Collected {count} companies for {c}")

# #     excel_path = generate_excel(leads)
# #     return leads, excel_path




# # # ---------------- SEARCH ----------------
# # from scraper.google_search_selenium import search_companies

# # # ---------------- SCRAPING & ENRICHMENT ----------------
# # from scraper.website_scraper import scrape_company
# # from scraper.linkedin_finder import find_linkedin

# # # ---------------- EXPORT ----------------
# # from services.excel_service import generate_excel

# # # ---------------- CONFIG ----------------
# # from config.regions import REGIONS

# # # ---------------- UTILS ----------------
# # from urllib.parse import urlparse
# # import time
# # from concurrent.futures import ThreadPoolExecutor, as_completed


# # # ======================================================
# # # KEYWORD PARSING
# # # ======================================================

# # def parse_keywords(raw_input):
# #     """
# #     Splits comma-separated keywords and returns:
# #     - list of individual keywords
# #     - combined keyword string
# #     """
# #     keywords = [k.strip() for k in raw_input.split(",") if k.strip()]
# #     combined = " ".join(keywords)
# #     return keywords, combined


# # # ======================================================
# # # REGION → COUNTRY RESOLUTION
# # # ======================================================

# # def resolve_countries(country, region=None):
# #     if region == "ALL":
# #         countries = []
# #         for group in REGIONS.values():
# #             countries.extend(group)
# #         return list(set(countries))

# #     if region in REGIONS:
# #         return REGIONS[region]

# #     return [country]


# # # ======================================================
# # # RETRY LOGIC
# # # ======================================================

# # def scrape_with_retry(url, retries=3, delay=3):
# #     for attempt in range(1, retries + 1):
# #         try:
# #             print(f"🔁 Attempt {attempt} for {url}")
# #             result = scrape_company(url)
# #             if result:
# #                 return result
# #         except Exception as e:
# #             print(f"⚠️ Error on attempt {attempt}: {e}")

# #         if attempt < retries:
# #             time.sleep(delay)

# #     return None


# # # ======================================================
# # # PARALLEL SCRAPE WORKER
# # # ======================================================

# # def scrape_worker(url, url_country, product):
# #     """
# #     Single-thread-safe scraping unit
# #     """
# #     parsed = urlparse(url)
# #     domain = parsed.netloc.lower().replace("www.", "")

# #     if not domain:
# #         return None

# #     company_data = scrape_with_retry(url)

# #     if not company_data:
# #         return None

# #     linkedin_url = find_linkedin(
# #         company_name=company_data.get("company_name"),
# #         website=url
# #     )

# #     company_data.update({
# #         "linkedin": linkedin_url,
# #         "product": product,
# #         "country": url_country,
# #         "domain": domain
# #     })

# #     return company_data


# # # ======================================================
# # # MAIN LEAD GENERATOR
# # # ======================================================

# # def generate_leads(product, country, company_types, limit, region=None):
# #     print("=== Lead generation started ===")
# #     print("Raw product input:", product)
# #     print("Region:", region)
# #     print("Country:", country)
# #     print("Company types:", company_types)
# #     print("Limit per country:", limit)

# #     leads = []
# #     seen_domains = set()
# #     country_lead_count = {}

# #     # 1. Parse keywords
# #     keywords, combined_query = parse_keywords(product)
# #     search_terms = keywords + [combined_query]

# #     print("Individual keywords:", keywords)
# #     print("Combined keyword:", combined_query)

# #     # 2. Resolve countries
# #     countries_to_search = resolve_countries(country, region)
# #     print("Countries to search:", countries_to_search)

# #     for c in countries_to_search:
# #         country_lead_count[c] = 0

# #     # 3. SEARCH PHASE (sequential, safe)
# #     all_company_urls = []

# #     for c in countries_to_search:
# #         for term in search_terms:
# #             urls = search_companies(
# #                 product=term,
# #                 country=c,
# #                 company_types=company_types,
# #                 limit=limit * 2  # over-collect
# #             )

# #             print(f"{c} | '{term}': {len(urls)} URLs found")

# #             all_company_urls.extend([(u, c) for u in urls])

# #             time.sleep(2)  # protect against Google blocking

# #     print(f"Total collected URLs: {len(all_company_urls)}")

# #     # 4. SCRAPING PHASE (PARALLEL)
# #     MAX_WORKERS = 5  # safe limit

# #     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
# #         futures = []

# #         for url, url_country in all_company_urls:
# #             if country_lead_count[url_country] >= limit:
# #                 continue

# #             futures.append(
# #                 executor.submit(scrape_worker, url, url_country, product)
# #             )

# #         for future in as_completed(futures):
# #             result = future.result()

# #             if not result:
# #                 continue

# #             domain = result["domain"]
# #             country_name = result["country"]

# #             if domain in seen_domains:
# #                 continue

# #             if country_lead_count[country_name] >= limit:
# #                 continue

# #             seen_domains.add(domain)
# #             leads.append(result)
# #             country_lead_count[country_name] += 1

# #             print(f"✅ {country_name}: {country_lead_count[country_name]}/{limit}")

# #     # 5. SUMMARY
# #     print("=== FINAL COUNTRY COUNTS ===")
# #     for c, count in country_lead_count.items():
# #         print(f"{c}: {count}")

# #     print(f"Total leads collected: {len(leads)}")
# #     print(f"Unique domains collected: {len(seen_domains)}")

# #     # 6. EXPORT
# #     excel_path = generate_excel(leads)
# #     return leads, excel_path


