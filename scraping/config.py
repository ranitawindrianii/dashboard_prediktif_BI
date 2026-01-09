import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "configs", ".env"))

CONFIG = {
    "KEYWORDS": [k.strip() for k in os.getenv("KEYWORDS", "kekurangan gizi").split(",") if k.strip()],
    "BASE_URL": os.getenv("BASE_URL", "https://www.republika.co.id"),
    "OUT_DIR": os.getenv("OUT_DIR", "./data_raw"),
    "SLEEP_MIN": float(os.getenv("SLEEP_MIN", "1")),
    "SLEEP_MAX": float(os.getenv("SLEEP_MAX", "3")),
    "MAX_PAGES": int(os.getenv("MAX_PAGES", "5")),
}
