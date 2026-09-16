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
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
INDEX_FILE = BASE_DIR / "speech_index.json"
PROGRESS_FILE = LOGS_DIR / "scraping_progress.json"

def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_progress(completed_ids):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(completed_ids), f)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:\"<>|]', '_', name)[:60].strip()

def download_speech(speech_info, download_pdf=True, max_retries=3):
    speech_id = speech_info["id"]
    year = speech_info["year"]
    url = speech_info["url"]
    
    # Parse month and day
    date_parts = speech_info["date"].split("/")
    month = date_parts[1].zfill(2) if len(date_parts) > 1 else "01"
    day = date_parts[2].zfill(2) if len(date_parts) > 2 else "01"
    
    clean_title = sanitize_filename(speech_info.get("title", f"speech_{speech_id}"))
    folder_name = f"{year}{month}{day}_id{speech_id}_{clean_title}"
    speech_dir = DATA_DIR / str(year) / month / folder_name
    speech_dir.mkdir(parents=True, exist_ok=True)
    
    md_file = speech_dir / "content.md"
    meta_file = speech_dir / "metadata.json"
    html_file = speech_dir / "original.html"
    pdf_file = speech_dir / "document.pdf"
    
    # If already downloaded, skip
    if md_file.exists() and meta_file.exists():
        return True, speech_id, "already_exists"
        
    s = requests.Session(impersonate="chrome120")
    
    for attempt in range(1, max_retries + 1):
        try:
            r = s.get(url, timeout=30)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                
                # Extract Title
                page_title = soup.title.get_text(strip=True) if soup.title else speech_info.get("title", "")
                
                # Extract PDF Link
                pdf_url = None
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if ".pdf" in href.lower() or "دریافت PDF" in a.get_text():
                        if not href.startswith("http"):
                            pdf_url = f"https://farsi.khamenei.ir{href}" if href.startswith("/") else f"https://farsi.khamenei.ir/{href}"
                        else:
                            pdf_url = href
                        break
                        
                # Extract text content
                content_div = soup.find("div", class_="Content") or soup.find("div", class_=re.compile(r"content|body|speech|text", re.I))
                full_text = ""
                paragraphs = []
                
                if content_div:
                    for el in content_div.find_all(["p", "div"]):
                        txt = el.get_text(strip=True)
                        if txt and txt not in paragraphs and len(txt) > 2:
                            # Filter out PDF button text
                            if "[دریافت PDF]" in txt:
                                txt = txt.replace("[دریافت PDF]", "").strip()
                            if txt:
                                paragraphs.append(txt)
                    full_text = "\n\n".join(paragraphs)
                else:
                    full_text = soup.get_text(separator="\n\n", strip=True)
                    
                # Save original HTML
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(r.text)
                    
                # Save Markdown
                md_content = f"# {page_title}\n\n"
                md_content += f"- **شناسه**: {speech_id}\n"
                md_content += f"- **تاریخ**: {speech_info['date']}\n"
                md_content += f"- **منبع**: [{url}]({url})\n"
                if pdf_url:
                    md_content += f"- **فایل PDF**: [دانلود نسخه رسمی]({pdf_url})\n"
                md_content += f"\n---\n\n{full_text}\n"
                
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(md_content)
                    
                # Save Metadata JSON
                metadata = {
                    "id": speech_id,
                    "year": year,
                    "month": int(month),
                    "day": int(day),
                    "solar_date": speech_info["date"],
                    "title": page_title,
                    "url": url,
                    "pdf_url": pdf_url,
                    "has_pdf": pdf_url is not None,
                    "char_count": len(full_text),
                    "word_count": len(full_text.split()),
                    "download_timestamp": time.time()
                }
                
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                    
                # Download PDF if requested
                if download_pdf and pdf_url and not pdf_file.exists():
                    try:
                        r_pdf = s.get(pdf_url, timeout=30)
                        if r_pdf.status_code == 200:
                            with open(pdf_file, "wb") as f_pdf:
                                f_pdf.write(r_pdf.content)
                    except Exception as e_pdf:
                        print(f"[!] Warning: failed to download PDF {pdf_url}: {e_pdf}")
                        
                return True, speech_id, "success"
            else:
                time.sleep(2 * attempt)
        except Exception as e:
            time.sleep(2 * attempt)
            
    return False, speech_id, "failed"

def download_all_speeches(max_workers=8, download_pdf=True):
    if not INDEX_FILE.exists():
        print("[-] Index file not found! Run crawler first.")
        return
        
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        speeches = json.load(f)
        
    completed_ids = load_progress()
    pending = [s for s in speeches if s["id"] not in completed_ids]
    
    print(f"[*] Total indexed speeches: {len(speeches)}")
    print(f"[*] Already completed: {len(completed_ids)}")
    print(f"[*] Pending download: {len(pending)}")
    
    if not pending:
        print("[+] All speeches already downloaded!")
        return
        
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_speech, s, download_pdf): s["id"] for s in pending}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading speeches"):
            success, speech_id, status = future.result()
            if success:
                completed_ids.add(speech_id)
                if len(completed_ids) % 20 == 0:
                    save_progress(completed_ids)
                    
    save_progress(completed_ids)
    print(f"[+] Download batch completed. Total finished: {len(completed_ids)}")

if __name__ == "__main__":
    download_all_speeches()
