from urllib.parse import urlparse
import time

from scraper.google_search_selenium import search_companies
from scraper.website_scraper import scrape_company
from scraper.linkedin_finder import find_linkedin
from services.excel_service import generate_excel
from config.regions import REGIONS

BAD_EXTENSIONS = (".pdf", ".doc", ".xls", ".zip")
DELAY = 1.2


def is_valid_url(url):
    parsed = urlparse(url)
    if not parsed.netloc:
        return False
    if parsed.netloc.endswith(".cn"):
        return False
    if any(url.lower().endswith(e) for e in BAD_EXTENSIONS):
        return False
    return True


def resolve_countries(country, region):
    if region and region in REGIONS:
        return REGIONS[region]
    if country:
        return [country]
    return []


def generate_leads(product, country, company_types, limit, region=None):
    product_terms = [p.strip() for p in product.split(",") if p.strip()]
    countries = resolve_countries(country, region)

    leads = []
    seen_domains = set()

    for c in countries:
        print(f"\n🌍 Country: {c}")
        count = 0

        for term in product_terms:
            for ctype in company_types:
                if count >= limit:
                    break

                urls = search_companies(
                    product=term,
                    country=c,
                    company_types=[ctype],
                    max_results=limit * 5
                )

                for url in urls:
                    if count >= limit:
                        break

                    if not is_valid_url(url):
                        continue

                    domain = urlparse(url).netloc.replace("www.", "")
                    if domain in seen_domains:
                        continue

                    data = scrape_company(url)

                    # 🇨🇳 Final China exclusion (content based)
                    if ".cn" in domain:
                        continue

                    data["linkedin"] = find_linkedin(
                        company_name=data["company_name"],
                        website=url
                    )

                    data["country"] = c
                    data["products"] = term
                    data["domain"] = domain

                    seen_domains.add(domain)
                    leads.append(data)
                    count += 1

                    print(f"✅ {count}/{limit}: {data['company_name']}")

                time.sleep(DELAY)

        print(f"✔ Collected {count} companies for {c}")

    excel_path = generate_excel(leads)
    return leads, excel_path




# # ---------------- SEARCH ----------------
# from scraper.google_search_selenium import search_companies

# # ---------------- SCRAPING & ENRICHMENT ----------------
# from scraper.website_scraper import scrape_company
# from scraper.linkedin_finder import find_linkedin

# # ---------------- EXPORT ----------------
# from services.excel_service import generate_excel

# # ---------------- CONFIG ----------------
# from config.regions import REGIONS

# # ---------------- UTILS ----------------
# from urllib.parse import urlparse
# import time
# from concurrent.futures import ThreadPoolExecutor, as_completed


# # ======================================================
# # KEYWORD PARSING
# # ======================================================

# def parse_keywords(raw_input):
#     """
#     Splits comma-separated keywords and returns:
#     - list of individual keywords
#     - combined keyword string
#     """
#     keywords = [k.strip() for k in raw_input.split(",") if k.strip()]
#     combined = " ".join(keywords)
#     return keywords, combined


# # ======================================================
# # REGION → COUNTRY RESOLUTION
# # ======================================================

# def resolve_countries(country, region=None):
#     if region == "ALL":
#         countries = []
#         for group in REGIONS.values():
#             countries.extend(group)
#         return list(set(countries))

#     if region in REGIONS:
#         return REGIONS[region]

#     return [country]


# # ======================================================
# # RETRY LOGIC
# # ======================================================

# def scrape_with_retry(url, retries=3, delay=3):
#     for attempt in range(1, retries + 1):
#         try:
#             print(f"🔁 Attempt {attempt} for {url}")
#             result = scrape_company(url)
#             if result:
#                 return result
#         except Exception as e:
#             print(f"⚠️ Error on attempt {attempt}: {e}")

#         if attempt < retries:
#             time.sleep(delay)

#     return None


# # ======================================================
# # PARALLEL SCRAPE WORKER
# # ======================================================

# def scrape_worker(url, url_country, product):
#     """
#     Single-thread-safe scraping unit
#     """
#     parsed = urlparse(url)
#     domain = parsed.netloc.lower().replace("www.", "")

#     if not domain:
#         return None

#     company_data = scrape_with_retry(url)

#     if not company_data:
#         return None

#     linkedin_url = find_linkedin(
#         company_name=company_data.get("company_name"),
#         website=url
#     )

#     company_data.update({
#         "linkedin": linkedin_url,
#         "product": product,
#         "country": url_country,
#         "domain": domain
#     })

#     return company_data


# # ======================================================
# # MAIN LEAD GENERATOR
# # ======================================================

# def generate_leads(product, country, company_types, limit, region=None):
#     print("=== Lead generation started ===")
#     print("Raw product input:", product)
#     print("Region:", region)
#     print("Country:", country)
#     print("Company types:", company_types)
#     print("Limit per country:", limit)

#     leads = []
#     seen_domains = set()
#     country_lead_count = {}

#     # 1. Parse keywords
#     keywords, combined_query = parse_keywords(product)
#     search_terms = keywords + [combined_query]

#     print("Individual keywords:", keywords)
#     print("Combined keyword:", combined_query)

#     # 2. Resolve countries
#     countries_to_search = resolve_countries(country, region)
#     print("Countries to search:", countries_to_search)

#     for c in countries_to_search:
#         country_lead_count[c] = 0

#     # 3. SEARCH PHASE (sequential, safe)
#     all_company_urls = []

#     for c in countries_to_search:
#         for term in search_terms:
#             urls = search_companies(
#                 product=term,
#                 country=c,
#                 company_types=company_types,
#                 limit=limit * 2  # over-collect
#             )

#             print(f"{c} | '{term}': {len(urls)} URLs found")

#             all_company_urls.extend([(u, c) for u in urls])

#             time.sleep(2)  # protect against Google blocking

#     print(f"Total collected URLs: {len(all_company_urls)}")

#     # 4. SCRAPING PHASE (PARALLEL)
#     MAX_WORKERS = 5  # safe limit

#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         futures = []

#         for url, url_country in all_company_urls:
#             if country_lead_count[url_country] >= limit:
#                 continue

#             futures.append(
#                 executor.submit(scrape_worker, url, url_country, product)
#             )

#         for future in as_completed(futures):
#             result = future.result()

#             if not result:
#                 continue

#             domain = result["domain"]
#             country_name = result["country"]

#             if domain in seen_domains:
#                 continue

#             if country_lead_count[country_name] >= limit:
#                 continue

#             seen_domains.add(domain)
#             leads.append(result)
#             country_lead_count[country_name] += 1

#             print(f"✅ {country_name}: {country_lead_count[country_name]}/{limit}")

#     # 5. SUMMARY
#     print("=== FINAL COUNTRY COUNTS ===")
#     for c, count in country_lead_count.items():
#         print(f"{c}: {count}")

#     print(f"Total leads collected: {len(leads)}")
#     print(f"Unique domains collected: {len(seen_domains)}")

#     # 6. EXPORT
#     excel_path = generate_excel(leads)
#     return leads, excel_path


