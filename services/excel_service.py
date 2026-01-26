import os
import re
import pandas as pd
import uuid

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

    # 🔒 TEMP FILE (prevents Windows lock issues)
    temp_path = path.replace(".xlsx", f"_{uuid.uuid4().hex}.xlsx")

    try:
        if os.path.exists(path):
            df_existing = pd.read_excel(path, engine="openpyxl")
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_final = df_new

        df_final.to_excel(temp_path, index=False, engine="openpyxl")

        # 🔁 Atomic replace (Windows safe)
        os.replace(temp_path, path)

    except PermissionError:
        # fallback — never crash the scraper
        fallback = path.replace(".xlsx", "_recovered.xlsx")
        df_new.to_excel(fallback, index=False, engine="openpyxl")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return path