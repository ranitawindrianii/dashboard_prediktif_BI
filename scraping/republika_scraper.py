import os
import time
import random
import json
import re
from datetime import datetime
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
from config import CONFIG

ua = UserAgent()

def make_headers():
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

def search_url(query, page=1):
    # Republika uses query params, keep this flexible (adjust if repo has helpers)
    params = {"search": query, "page": page}
    return f"{CONFIG['BASE_URL']}/search?{urlencode(params)}"

def clean_text(t: str) -> str:
    if not t:
        return ""
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def parse_article(url: str) -> dict:
    resp = requests.get(url, headers=make_headers(), timeout=20)
    if resp.status_code != 200:
        return {"url": url, "status": resp.status_code, "error": "fetch_failed"}

    soup = BeautifulSoup(resp.text, "lxml")

    # Try multiple common patterns
    title = soup.select_one("h1") or soup.select_one("h2.entry-title") or soup.select_one("h1.article-title")
    title = clean_text(title.get_text()) if title else None

    # Republika often uses 'article' tag or a content container
    content_node = soup.select_one("article") or soup.select_one(".detail-article") or soup.select_one(".text-article")
    content = clean_text(content_node.get_text()) if content_node else None

    # Date and author heuristics
    date_node = soup.select_one("time") or soup.select_one(".date") or soup.select_one(".publish-date")
    date_text = clean_text(date_node.get_text()) if date_node else None

    author_node = soup.select_one(".author") or soup.select_one(".reporter") or soup.select_one(".redaksi")
    author = clean_text(author_node.get_text()) if author_node else None

    return {
        "url": url,
        "title": title,
        "content": content,
        "date_raw": date_text,
        "author": author,
        "scraped_at": datetime.utcnow().isoformat(),
    }

def extract_results(soup):
    # Flexible selectors for search result listings
    cards = soup.select("article a") or soup.select(".story a") or soup.select(".list-news a")
    urls = []
    for a in cards:
        href = a.get("href")
        if not href:
            continue
        # Filter only article-like URLs
        if "republika.co.id" in href and not href.endswith("/search") and len(href) > 20:
            urls.append(href)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            unique.append(u)
            seen.add(u)
    return unique

def scrape_keyword(keyword: str, out_dir: str, max_pages: int):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"republika_{keyword.replace(' ', '_')}.ndjson")

    with open(out_path, "a", encoding="utf-8") as f:
        for page in tqdm(range(1, max_pages + 1), desc=f"Keyword='{keyword}'"):
            url = search_url(keyword, page)
            resp = requests.get(url, headers=make_headers(), timeout=20)
            if resp.status_code != 200:
                time.sleep(random.uniform(CONFIG["SLEEP_MIN"], CONFIG["SLEEP_MAX"]))
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            article_urls = extract_results(soup)

            for aurl in article_urls:
                data = parse_article(aurl)
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
                time.sleep(random.uniform(CONFIG["SLEEP_MIN"], CONFIG["SLEEP_MAX"]))

            time.sleep(random.uniform(CONFIG["SLEEP_MIN"], CONFIG["SLEEP_MAX"]))

def main():
    for kw in CONFIG["KEYWORDS"]:
        scrape_keyword(kw, CONFIG["OUT_DIR"], CONFIG["MAX_PAGES"])

if __name__ == "__main__":
    main()
