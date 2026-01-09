# save as step_1_bronze_ingest.py
import os
import shutil

SRC_DIR = "scrapper_result"
BRONZE_DIR = "lakehouse/bronze"
os.makedirs(BRONZE_DIR, exist_ok=True)

files = [
    "keyword_search.csv",
    "search_results.csv",
    "article_metadata.csv"
]

for f in files:
    src = os.path.join(SRC_DIR, f)
    dst = os.path.join(BRONZE_DIR, f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied {src} -> {dst}")
    else:
        print(f"Warning: {src} not found")
