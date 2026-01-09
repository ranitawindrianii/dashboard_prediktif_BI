import os
import time
import random
import json
from datetime import datetime, UTC
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

# Konfigurasi dasar
BASE_URL = "https://www.republika.co.id"
KEYWORDS = ["kekurangan gizi"]   # bisa ditambah: "stunting", "MBG", dll
OUT_DIR = "./data_raw"
MAX_PAGES = 3                    # jumlah halaman pencarian per keyword
SLEEP_MIN, SLEEP_MAX = 1, 3      # jeda antar request

os.makedirs(OUT_DIR, exist_ok=True)

def search_url(query, page=1):
    params = {"search": query, "page": page}
    return f"{BASE_URL}/search?{urlencode(params)}"

def clean_text(t: str) -> str:
    if not t:
        return ""
    return " ".join(t.split()).strip()

def parse_article(url: str) -> dict:
    try:
        resp = requests.get(url, timeout=20)
        if resp.status_code != 200:
            return {"url": url, "status": resp.status_code, "error": "fetch_failed"}

        soup = BeautifulSoup(resp.text, "lxml")

        title_node = soup.select_one("h1")
        title = clean_text(title_node.get_text()) if title_node else None

        content_node = soup.select_one("article") or soup.select_one(".detail-article")
        content = clean_text(content_node.get_text()) if content_node else None

        date_node = soup.select_one("time") or soup.select_one(".date")
        date_text = clean_text(date_node.get_text()) if date_node else None

        author_node = soup.select_one(".author") or soup.select_one(".reporter")
        author = clean_text(author_node.get_text()) if author_node else None

        return {
            "url": url,
            "title": title,
            "content": content,
            "date_raw": date_text,
            "author": author,
            "scraped_at": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {"url": url, "error": str(e)}

def extract_results(soup):
    # ambil semua link dari hasil pencarian
    cards = soup.select("a")
    urls = []
    for a in cards:
        href = a.get("href")
        if href and "republika.co.id" in href and not href.endswith("/search"):
            urls.append(href)
    return list(dict.fromkeys(urls))  # dedup

def scrape_keyword(keyword: str):
    out_path = os.path.join(OUT_DIR, f"republika_{keyword.replace(' ', '_')}.ndjson")
    with open(out_path, "a", encoding="utf-8") as f:
        for page in range(1, MAX_PAGES + 1):
            url = search_url(keyword, page)
            print(f"[INFO] Scraping search page: {url}")
            resp = requests.get(url, timeout=20)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            article_urls = extract_results(soup)
            print(f"[INFO] Found {len(article_urls)} articles")

            for aurl in article_urls:
                data = parse_article(aurl)
                if data.get("title") and data.get("content"):
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))

def main():
    for kw in KEYWORDS:
        scrape_keyword(kw)

if __name__ == "__main__":
    main()
