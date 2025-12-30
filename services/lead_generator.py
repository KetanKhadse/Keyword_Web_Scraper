# Search
from scraper.google_search_selenium import search_companies

# Scraping & enrichment
from scraper.website_scraper import scrape_company
from scraper.linkedin_finder import find_linkedin

# Export
from services.excel_service import generate_excel

# Config
from config.regions import REGIONS

# Utils
from urllib.parse import urlparse
import time


# ---------------- COUNTRY RESOLUTION ----------------

def resolve_countries(country, region=None):
    """
    Expands region into countries.
    """
    if region == "ALL":
        countries = []
        for c_list in REGIONS.values():
            countries.extend(c_list)
        return list(set(countries))

    if region in REGIONS:
        return REGIONS[region]

    return [country]


# ---------------- RETRY LOGIC ----------------

def scrape_with_retry(url, retries=3, delay=3):
    for attempt in range(1, retries + 1):
        try:
            print(f"🔁 Attempt {attempt} for {url}")
            result = scrape_company(url)
            if result:
                return result
        except Exception as e:
            print(f"⚠️ Error on attempt {attempt}: {e}")

        if attempt < retries:
            time.sleep(delay)

    return None


# ---------------- MAIN GENERATOR ----------------

def generate_leads(product, country, company_types, limit, region=None):
    print("=== Lead generation started ===")
    print("Product:", product)
    print("Country:", country)
    print("Region:", region)
    print("Company types:", company_types)
    print("Limit:", limit)

    leads = []
    seen_domains = set()

    # 1. Resolve countries
    countries_to_search = resolve_countries(country, region)
    print(f"Countries to search: {countries_to_search}")

    # 2. Search phase (OVER-COLLECT URLS)
    all_company_urls = []

    for c in countries_to_search:
        urls = search_companies(
            product=product,
            country=c,
            company_types=company_types,
            limit=limit * 2  # over-collect
        )

        print(f"{c}: {len(urls)} URLs found")
        all_company_urls.extend([(u, c) for u in urls])

        time.sleep(2)

    print(f"Total collected URLs: {len(all_company_urls)}")

    # 3. Scrape phase
    for url, url_country in all_company_urls:
        print("Scraping:", url)

        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")

        if not domain:
            continue

        if domain in seen_domains:
            print("🔁 Skipping duplicate domain:", domain)
            continue

        company_data = scrape_with_retry(url)

        if not company_data:
            print("❌ Failed after retries:", url)
            continue

        print("✅ Scraped:", company_data.get("company_name"))

        linkedin_url = find_linkedin(
            company_name=company_data.get("company_name"),
            website=url
        )

        # Enrich
        company_data.update({
            "linkedin": linkedin_url,
            "product": product,
            "country": url_country,
            "domain": domain
        })

        seen_domains.add(domain)
        leads.append(company_data)

        if len(leads) >= limit:
            break

    print(f"Final leads count: {len(leads)}")
    print(f"Unique domains collected: {len(seen_domains)}")

    # 4. Export
    excel_path = generate_excel(leads)

    return leads, excel_path
