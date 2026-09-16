# -*- coding: utf-8 -*-
import sys
import json
import time
import os
import re
import random
from pathlib import Path
from curl_cffi import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
INDEX_FILE = BASE_DIR / "speech_index.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

START_YEAR = 1357
END_YEAR = 1404

def load_existing_index():
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {item["id"]: item for item in data}
        except Exception:
            return {}
    return {}

def save_index(index_dict):
    sorted_items = sorted(list(index_dict.values()), key=lambda x: (x["year"], x.get("date", ""), x["id"]))
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_items, f, ensure_ascii=False, indent=2)

def fetch_year_speeches(year, max_retries=5):
    url = f"https://farsi.khamenei.ir/speech?year={year}"
    speeches = []
    
    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(random.uniform(0.5, 1.2))
            s = requests.Session(impersonate="chrome120")
            r = s.get(url, timeout=40)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "speech-content" in href:
                        text = a.get_text(strip=True)
                        m_id = re.search(r"id=(\d+)", href)
                        if m_id:
                            speech_id = int(m_id.group(1))
                            m_date = re.match(r"^(\d{4}/\d{1,2}/\d{1,2})[-|\s]*(.*)", text)
                            if m_date:
                                date_str = m_date.group(1)
                                title_str = m_date.group(2).strip()
                            else:
                                date_str = f"{year}/01/01"
                                title_str = text
                            
                            speeches.append({
                                "id": speech_id,
                                "year": year,
                                "date": date_str,
                                "title": title_str,
                                "url": f"https://farsi.khamenei.ir/speech-content?id={speech_id}"
                            })
                print(f"[+] Year {year}: Discovered {len(speeches)} speeches.")
                return speeches
            elif r.status_code == 404:
                print(f"[-] Year {year}: 404 Not Found.")
                return []
            else:
                print(f"[-] Year {year} HTTP {r.status_code} (attempt {attempt}/{max_retries})")
                time.sleep(2 * attempt)
        except Exception as e:
            print(f"[-] Year {year} attempt {attempt}/{max_retries} error: {e}")
            time.sleep(3 * attempt)
            
    return speeches

def crawl_missing_years():
    index_dict = load_existing_index()
    covered_years = set(item["year"] for item in index_dict.values())
    all_years = list(range(START_YEAR, END_YEAR + 1))
    
    target_years = [y for y in all_years if y not in covered_years]
    print(f"[*] Total missing years to crawl: {len(target_years)}.")
    
    new_found = 0
    for year in target_years:
        print(f"[*] Crawling year {year}...")
        speeches = fetch_year_speeches(year)
        if speeches:
            for s in speeches:
                if s["id"] not in index_dict:
                    index_dict[s["id"]] = s
                    new_found += 1
            save_index(index_dict)
            print(f"[+] Year {year} indexed. Total unique speeches: {len(index_dict)}")
            
    print(f"[+] Missing years crawl completed. Added: {new_found}, Total: {len(index_dict)}")
    return len(index_dict)

if __name__ == "__main__":
    crawl_missing_years()
