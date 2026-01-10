import pandas as pd
import os
from datetime import datetime
import re


# ================== EXCEL SAFETY CONSTANTS ==================

INVALID_XML_CHARS = re.compile(
    r"[\x00-\x08\x0B\x0C\x0E-\x1F]"
)

MAX_CELL_LENGTH = 32767  # Excel hard limit


# ================== CLEANER ==================

def clean_excel_text(value):
    """
    Makes any value safe for Excel XML
    """
    if value is None:
        return ""

    # Preserve numbers / booleans
    if isinstance(value, (int, float, bool)):
        return value

    value = str(value)

    # Remove illegal XML characters
    value = INVALID_XML_CHARS.sub("", value)

    # Kill PDF headers if accidentally scraped
    if value.lstrip().startswith("%PDF"):
        return ""

    # Normalize whitespace
    value = (
        value.replace("\u00a0", " ")
             .replace("\r", " ")
             .replace("\n", " ")
             .strip()
    )

    # Truncate long cells (prevents Excel crash)
    if len(value) > MAX_CELL_LENGTH:
        value = value[:MAX_CELL_LENGTH - 3] + "..."

    return value


# ================== EXCEL GENERATOR ==================

def generate_excel(leads):
    if not leads:
        return None

    cleaned_leads = []

    for lead in leads:
        cleaned = {}
        for k, v in lead.items():
            cleaned[k] = clean_excel_text(v)
        cleaned_leads.append(cleaned)

    df = pd.DataFrame(cleaned_leads)

    os.makedirs("data/output", exist_ok=True)

    filename = f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    path = os.path.join("data/output", filename)

    # Write Excel safely
    df.to_excel(
        path,
        index=False,
        engine="openpyxl"
    )

    return path


# import pandas as pd
# import os
# from datetime import datetime
# import re


# def clean_excel_text(value):
#     if value is None:
#         return ""

#     if not isinstance(value, str):
#         return str(value)

#     # Remove binary / control characters
#     value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)

#     # Kill PDF headers if accidentally scraped
#     if value.lstrip().startswith("%PDF"):
#         return ""

#     return value.strip()


# def generate_excel(leads):
#     if not leads:
#         return None

#     cleaned_leads = []

#     for lead in leads:
#         cleaned = {}
#         for k, v in lead.items():
#             cleaned[k] = clean_excel_text(v)
#         cleaned_leads.append(cleaned)

#     df = pd.DataFrame(cleaned_leads)

#     os.makedirs("data/output", exist_ok=True)

#     filename = f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
#     path = os.path.join("data/output", filename)

#     df.to_excel(path, index=False, engine="openpyxl")

#     return path
