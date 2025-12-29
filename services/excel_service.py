import pandas as pd
import os
from datetime import datetime


def generate_excel(leads):
    if not leads:
        return None

    df = pd.DataFrame(leads)

    os.makedirs("data/output", exist_ok=True)

    filename = f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    path = os.path.join("data/output", filename)

    df.to_excel(path, index=False)

    return path
