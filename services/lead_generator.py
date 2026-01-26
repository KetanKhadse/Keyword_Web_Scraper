from urllib.parse import urlparse
import time

from scraper.google_search_selenium import search_companies
from scraper.website_scraper import scrape_company
from scraper.linkedin_finder import find_linkedin
from services.excel_service import generate_excel
from config.regions import REGIONS


BAD_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip"
)

DELAY_BETWEEN_QUERIES = 1.5

CHINA_KEYWORDS = [
    "china", "prc", "shanghai", "shenzhen", "beijing", "guangzhou"
]

INDIA_KEYWORDS = [
    "india", "bharat", "mumbai", "delhi", "bangalore", "chennai"
]


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc:
        return False
    if any(url.lower().endswith(ext) for ext in BAD_EXTENSIONS):
        return False
    return True


def detect_affiliation(text: str, keywords: list[str]) -> bool:
    if not text:
        return False
    text = text.lower()
    return any(k in text for k in keywords)


def split_product_terms(product: str):
    return [p.strip() for p in product.split(",") if p.strip()]


def resolve_countries(country, region):
    if region and region in REGIONS:
        return REGIONS[region]
    if country:
        return [country]
    return []


def generate_leads(product, country, company_types, limit, region=None):
    print("=== Lead generation started ===")
    print("Limit per country:", limit)

    product_terms = split_product_terms(product)
    countries = resolve_countries(country, region)

    all_leads = []
    seen_domains = set()

    for c in countries:
        print(f"\n🌍 Country: {c}")
        country_leads = []
        collected = 0

        for term in product_terms:
            for ctype in company_types:
                if collected >= limit:
                    break

                urls = search_companies(
                    product=term,
                    country=c,
                    company_types=[ctype],
                    max_results=limit * 4
                )

                for url in urls:
                    if collected >= limit:
                        break

                    if not is_valid_url(url):
                        continue

                    domain = urlparse(url).netloc.lower().replace("www.", "")
                    if domain in seen_domains:
                        continue

                    data = scrape_company(url)

                    combined_text = " ".join([
                        data.get("company_name", ""),
                        data.get("footer_text", ""),
                        data.get("about_text", "")
                    ])

                    data["china_affiliation"] = detect_affiliation(
                        combined_text, CHINA_KEYWORDS
                    )
                    data["india_affiliation"] = detect_affiliation(
                        combined_text, INDIA_KEYWORDS
                    )

                    data["linkedin"] = find_linkedin(
                        company_name=data.get("company_name"),
                        website=url
                    )

                    data["products"] = term
                    data["country"] = c
                    data["domain"] = domain

                    country_leads.append(data)
                    all_leads.append(data)
                    seen_domains.add(domain)
                    collected += 1

                    print(f"✅ Added ({collected}/{limit}): {domain}")

                time.sleep(DELAY_BETWEEN_QUERIES)

        print(f"✔ Finished {c} ({collected} companies)")

        # 🚨 AUTO EXPORT PER COUNTRY (NO DATA LOSS)
        export_leads = []
        for lead in country_leads:
            clean = lead.copy()
            clean.pop("china_affiliation", None)
            clean.pop("india_affiliation", None)
            export_leads.append(clean)

        generate_excel(export_leads, country_name=c)

    print(f"\n✅ Total leads collected: {len(all_leads)}")
    return all_leads
