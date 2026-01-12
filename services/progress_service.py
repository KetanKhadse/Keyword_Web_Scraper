import json
import os

PROGRESS_FILE = "data/progress.json"


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {
            "seen_domains": [],
            "completed_countries": []
        }

    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(seen_domains, completed_countries):
    os.makedirs("data", exist_ok=True)

    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "seen_domains": list(seen_domains),
                "completed_countries": list(completed_countries),
            },
            f,
            indent=2
        )
