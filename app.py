import streamlit as st
import time

from config.countries import COUNTRIES
from config.company_types import COMPANY_TYPES
from config.limits import LIMITS
from services.lead_generator import generate_leads
from config.regions import REGIONS
# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Lead Generation Automation",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🔍 Lead Generation Automation Tool")
st.markdown(
    """
    Automate discovery of companies providing a specific product and extract  
    **Company Website, Email,Contact Details and LinkedIn details** for sales prospecting.
    """
)

st.divider()

# ---------------- INPUT SECTION ----------------
st.subheader("📥 Search Criteria")

col1, col2 = st.columns(2)

with col1:
    product = st.text_input(
        "Product",
        placeholder="e.g. Valve"
    )
    region = st.selectbox(
    "Target Region",
    options=["Single Country"] + list(REGIONS.keys()) + ["ALL"]
    )
    country = None
if region == "Single Country":
    country = st.selectbox("Select Country", COUNTRIES)






with col2:
    company_types = st.multiselect(
        "Company Type",
        options=COMPANY_TYPES
    )

    limit = st.selectbox(
        "Result Limit",
        options=LIMITS,
        index=1
    )

# ---------------- ACTION BUTTON ----------------
st.divider()

start_btn = st.button("🚀 Start Lead Generation", use_container_width=True)

# ---------------- PROCESSING ----------------
if start_btn:
    if not product.strip() or not company_types:
        st.error("Please fill all required fields.")
        st.stop()

    with st.spinner("Generating leads..."):
        leads, excel_path = generate_leads(
            product=product,
            country=country,
            company_types=company_types,
            limit=limit,
            region= region
        )

    if not leads:
        st.warning("No leads found.")
        st.stop()

    st.success(f"Found {len(leads)} companies")

    st.dataframe(leads, use_container_width=True)

    with open(excel_path, "rb") as f:
        st.download_button(
            "⬇️ Download Excel",
            data=f,
            file_name="leads.xlsx"
        )

