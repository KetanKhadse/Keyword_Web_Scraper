from services.lead_generator import generate_leads

if __name__ == "__main__":
    output_path = generate_leads(
        product="solar panel, inverter",
        country="Germany",
        company_types=["manufacturer", "supplier"],
        limit=200,
        region=None
    )

    print("✅ Scraping finished")
    print("📁 Output saved at:", output_path)
