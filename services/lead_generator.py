# from scraper.duckduckgo_search import search_companies
from scraper.google_search_selenium import search_companies
from scraper.website_scraper import scrape_company
from scraper.linkedin_finder import find_linkedin
from services.excel_service import generate_excel

from urllib.parse import urlparse


def generate_leads(product, country, company_types, limit):
    print("=== Lead generation started ===")
    print("Product:", product)
    print("Country:", country)
    print("Company types:", company_types)
    print("Limit:", limit)

    leads = []
    seen_domains = set()

    # 1. Search companies
    company_urls = search_companies(
        product=product,
        country=country,
        company_types=company_types,
        limit=limit
    )

    print(f"Found {len(company_urls)} URLs")
    print(company_urls[:5])  # show first few URLs

    # 2. Scrape each company
    for url in company_urls:
        print("Scraping:", url)

        # Normalize domain for uniqueness
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")

        if not domain:
            print("❌ Invalid URL:", url)
            continue

        if domain in seen_domains:
            print("🔁 Skipping duplicate domain:", domain)
            continue

        # Scrape company website
        company_data = scrape_company(url)

        if not company_data:
            print("❌ Failed to scrape:", url)
            continue

        print("✅ Scraped:", company_data.get("company_name"))

        # Find LinkedIn
        linkedin_url = find_linkedin(
            company_name=company_data.get("company_name"),
            website=url
        )

        # Enrich data
        company_data["linkedin"] = linkedin_url
        company_data["product"] = product
        company_data["country"] = country
        company_data["domain"] = domain

        # Save
        seen_domains.add(domain)
        leads.append(company_data)

        if len(leads) >= limit:
            break

    print(f"Final leads count: {len(leads)}")
    print(f"Unique domains collected: {len(seen_domains)}")

    # 3. Export to Excel
    excel_path = generate_excel(leads)

    return leads, excel_path
