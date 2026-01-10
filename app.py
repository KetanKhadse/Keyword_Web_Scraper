import streamlit as st
from services.lead_generator import generate_leads
from config.countries import COUNTRIES
from config.company_types import COMPANY_TYPES
from config.limits import LIMITS
from config.regions import REGIONS
import os

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
    **Company Website, Email, Phone and LinkedIn details**.
    """
)

st.divider()

# ---------------- INPUT SECTION ----------------
st.subheader("📥 Search Criteria")

col1, col2 = st.columns(2)

with col1:
    product = st.text_input(
        "Product",
        placeholder="e.g. Industrial Valve"
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

st.divider()

# ---------------- ACTION BUTTON ----------------
start_btn = st.button("🚀 Start Lead Generation", width='stretch')

# ---------------- PROCESSING ----------------
if start_btn:

    # -------- Validation --------
    if not product.strip():
        st.error("Please enter a product name.")
        st.stop()

    if not company_types:
        st.error("Please select at least one company type.")
        st.stop()

    # -------- Prevent duplicate Streamlit runs --------
    if "running" not in st.session_state:
        st.session_state.running = False

    if st.session_state.running:
        st.warning("Lead generation is already running. Please wait.")
        st.stop()

    st.session_state.running = True

    # -------- Run backend --------
    with st.spinner("Generating leads..."):
        leads, excel_path = generate_leads(
            product=product.strip(),
            country=country,
            company_types=company_types,
            limit=limit,
            region=None if region == "Single Country" else region
        )

    st.session_state.running = False

    # -------- Results --------
    if not leads:
        st.warning("No leads found.")
        st.stop()

    st.success(f"Found {len(leads)} companies")
    st.dataframe(leads, width='stretch')

    # -------- Excel download (SAFE) --------
    if excel_path and os.path.exists(excel_path):
        with open(excel_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Excel",
                data=f,
                file_name=os.path.basename(excel_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("Excel file could not be generated.")
