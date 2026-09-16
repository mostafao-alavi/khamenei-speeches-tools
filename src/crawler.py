# -*- coding: utf-8 -*-
import sys
import json
import time
import os
import re
from pathlib import Path
from curl_cffi import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
INDEX_FILE = BASE_DIR / "speech_index.json"

START_YEAR = 1357
END_YEAR = 1404

def fetch_year_speeches(year, max_retries=3):
    url = f"https://farsi.khamenei.ir/speech?year={year}"
    for attempt in range(1, max_retries + 1):
        try:
            s = requests.Session(impersonate="chrome120")
            r = s.get(url, timeout=30)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                speeches = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "speech-content" in href:
                        text = a.get_text(strip=True)
                        m_id = re.search(r"id=(\d+)", href)
                        if m_id:
                            speech_id = int(m_id.group(1))
                            # Parse date if available in text (e.g. '1390/12/18- ...')
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
                print(f"[+] Year {year}: Found {len(speeches)} speeches.")
                return speeches
            else:
                print(f"[-] Year {year} HTTP status: {r.status_code} (attempt {attempt}/{max_retries})")
        except Exception as e:
            print(f"[-] Year {year} error on attempt {attempt}/{max_retries}: {e}")
            time.sleep(2 * attempt)
    return []

def crawl_all_years(start_year=START_YEAR, end_year=END_YEAR, max_workers=5):
    print(f"[*] Starting speech discovery from year {start_year} to {end_year}...")
    all_speeches = {}
    years = list(range(start_year, end_year + 1))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_year = {executor.submit(fetch_year_speeches, y): y for y in years}
        for future in as_completed(future_to_year):
            year = future_to_year[future]
            try:
                speeches = future.result()
                for sp in speeches:
                    all_speeches[sp["id"]] = sp
            except Exception as e:
                print(f"[!] Exception for year {year}: {e}")
                
    speeches_list = sorted(list(all_speeches.values()), key=lambda x: (x["year"], x["date"], x["id"]))
    print(f"[*] Discovery complete! Total unique speeches found: {len(speeches_list)}")
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(speeches_list, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved index to {INDEX_FILE}")
    return speeches_list

if __name__ == "__main__":
    crawl_all_years()
