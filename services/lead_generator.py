# from scraper.duckduckgo_search import search_companies
from scraper.google_search_selenium import search_companies
from scraper.website_scraper import scrape_company
from scraper.linkedin_finder import find_linkedin
from services.excel_service import generate_excel


def generate_leads(product, country, company_types, limit):
    print("=== Lead generation started ===")
    print("Product:", product)
    print("Country:", country)
    print("Company types:", company_types)
    print("Limit:", limit)

    leads = []

    # 1. Search companies
    company_urls = search_companies(
        product=product,
        country=country,
        company_types=company_types,
        limit=limit
    )

    print(f"Found {len(company_urls)} URLs")
    print(company_urls[:5])  # show first few

    # 2. Scrape each company
    for url in company_urls:
        print("Scraping:", url)

        company_data = scrape_company(url)

        if not company_data:
            print("❌ Failed to scrape:", url)
            continue

        print("✅ Scraped:", company_data["company_name"])

        linkedin_url = find_linkedin(
            company_name=company_data["company_name"],
            website=url
        )

        company_data["linkedin"] = linkedin_url
        company_data["product"] = product
        company_data["country"] = country

        leads.append(company_data)

        if len(leads) >= limit:
            break

    print(f"Final leads count: {len(leads)}")

    excel_path = generate_excel(leads)

    return leads, excel_path
