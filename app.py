import streamlit as st
from services.lead_generator import generate_leads
from services.progress_service import save_progress
from config.countries import COUNTRIES
from config.company_types import COMPANY_TYPES
from config.limits import LIMITS
from config.regions import REGIONS
import os
import pandas as pd

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
    product = st.text_input("Product", placeholder="e.g. Industrial Valve")

    region = st.selectbox(
        "Target Region",
        options=["Single Country"] + list(REGIONS.keys()) + ["ALL"]
    )

    country = None
    if region == "Single Country":
        country = st.selectbox("Select Country", COUNTRIES)

with col2:
    company_types = st.multiselect("Company Type", options=COMPANY_TYPES)

    limit = st.selectbox(
        "Result Limit",
        options=LIMITS,
        index=1
    )

st.divider()

# ---------------- ACTION BUTTON ----------------
start_btn = st.button("🚀 Start Lead Generation", use_container_width=True)

# ---------------- PROCESSING ----------------
if start_btn:

    if not product.strip():
        st.error("Please enter a product name.")
        st.stop()

    if not company_types:
        st.error("Please select at least one company type.")
        st.stop()

    # 🔥 RESET PROGRESS PER RUN (FIX)
    save_progress(set(), set())

    with st.spinner("Generating leads (safe & resumable)..."):
        excel_path = generate_leads(
            product=product.strip(),
            country=country,
            company_types=company_types,
            limit=limit,
            region=None if region == "Single Country" else region
        )

    if not excel_path or not os.path.exists(excel_path):
        st.warning("No leads found.")
        st.stop()

    st.success("Lead generation completed.")

    files = sorted(f for f in os.listdir(excel_path) if f.endswith(".xlsx"))

    st.subheader("📂 Generated Country Files")

    for file in files:
        file_path = os.path.join(excel_path, file)

        with st.expander(f"📄 {file}"):
            try:
                with open(file_path, "rb") as f:
                 df = pd.read_excel(f)
                st.write(f"Rows: {len(df)}")
                st.dataframe(df, width="stretch")
            except Exception:
                st.warning("Could not preview file.")

            with open(file_path, "rb") as f:
                st.download_button(
                    f"⬇️ Download {file}",
                    data=f,
                    file_name=file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
