import os
import re
import pandas as pd

MAX_CELL_LENGTH = 32767
INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


def clean_excel_text(value):
    if value is None:
        return ""

    if isinstance(value, (int, float, bool)):
        return value

    value = str(value)
    value = INVALID_XML_CHARS.sub("", value)
    value = value.replace("\n", " ").replace("\r", " ").strip()

    if len(value) > MAX_CELL_LENGTH:
        value = value[: MAX_CELL_LENGTH - 3] + "..."

    return value


def normalize_country(country: str) -> str:
    return country.lower().replace(" ", "_")


def append_to_excel(rows, country: str):
    """
    Append leads into a country-specific Excel file.
    """
    if not rows:
        return None

    os.makedirs("data/output", exist_ok=True)

    filename = f"{normalize_country(country)}.xlsx"
    path = os.path.join("data/output", filename)

    cleaned_rows = [
        {k: clean_excel_text(v) for k, v in row.items()}
        for row in rows
    ]

    df_new = pd.DataFrame(cleaned_rows)

    if os.path.exists(path):
        try:
            df_existing = pd.read_excel(path, engine="openpyxl")
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        except Exception:
            fallback = path.replace(".xlsx", "_recovered.xlsx")
            df_new.to_excel(fallback, index=False, engine="openpyxl")
            return path
    else:
        df_final = df_new

    df_final.to_excel(path, index=False, engine="openpyxl")
    return path


# import os
# import re
# import pandas as pd

# OUTPUT_FILE = "data/output/leads_partial.xlsx"

# MAX_CELL_LENGTH = 32767
# INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


# def clean_excel_text(value):
#     try:
#         if value is None:
#             return ""

#         if isinstance(value, (int, float, bool)):
#             return value

#         value = str(value)
#         value = INVALID_XML_CHARS.sub("", value)
#         value = value.replace("\n", " ").replace("\r", " ").strip()

#         if len(value) > MAX_CELL_LENGTH:
#             value = value[: MAX_CELL_LENGTH - 3] + "..."

#         return value
#     except Exception:
#         return ""


# def append_to_excel(rows):
#     """
#     Safe incremental Excel writer.
#     Can be called repeatedly without data loss.
#     """
#     if not rows:
#         return

#     os.makedirs("data/output", exist_ok=True)

#     cleaned_rows = []
#     for row in rows:
#         cleaned_rows.append({k: clean_excel_text(v) for k, v in row.items()})

#     df_new = pd.DataFrame(cleaned_rows)

#     if os.path.exists(OUTPUT_FILE):
#         try:
#             df_existing = pd.read_excel(OUTPUT_FILE, engine="openpyxl")
#             df_final = pd.concat([df_existing, df_new], ignore_index=True)
#         except Exception:
#             # If file is locked or corrupted, write a fallback
#             fallback = OUTPUT_FILE.replace(".xlsx", "_recovered.xlsx")
#             df_new.to_excel(fallback, index=False, engine="openpyxl")
#             return
#     else:
#         df_final = df_new

#     df_final.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")

#================Last Working start===========================

# import pandas as pd
# import os
# from datetime import datetime
# import re


# # ================== EXCEL SAFETY CONSTANTS ==================

# INVALID_XML_CHARS = re.compile(
#     r"[\x00-\x08\x0B\x0C\x0E-\x1F]"
# )

# MAX_CELL_LENGTH = 32767  # Excel hard limit


# # ================== CLEANER ==================

# def clean_excel_text(value):
#     """
#     Makes any value safe for Excel XML
#     """
#     if value is None:
#         return ""

#     # Preserve numbers / booleans
#     if isinstance(value, (int, float, bool)):
#         return value

#     value = str(value)

#     # Remove illegal XML characters
#     value = INVALID_XML_CHARS.sub("", value)

#     # Kill PDF headers if accidentally scraped
#     if value.lstrip().startswith("%PDF"):
#         return ""

#     # Normalize whitespace
#     value = (
#         value.replace("\u00a0", " ")
#              .replace("\r", " ")
#              .replace("\n", " ")
#              .strip()
#     )

#     # Truncate long cells (prevents Excel crash)
#     if len(value) > MAX_CELL_LENGTH:
#         value = value[:MAX_CELL_LENGTH - 3] + "..."

#     return value


# # ================== EXCEL GENERATOR ==================

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

#     # Write Excel safely
#     df.to_excel(
#         path,
#         index=False,
#         engine="openpyxl"
#     )

#     return path
#================Last Working End===========================




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
