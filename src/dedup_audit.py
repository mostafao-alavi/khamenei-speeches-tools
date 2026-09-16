# -*- coding: utf-8 -*-
import sys
import json
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
INDEX_FILE = BASE_DIR / "speech_index.json"
PROGRESS_FILE = LOGS_DIR / "scraping_progress.json"

ANALYSIS_KEYWORDS = [
    "تحلیل", "یادداشت", "گزارش خبری", "گزیده", "عکس‌نوشت", "نماهنگ", "اطلاع‌نگاشت",
    "برش‌هایی از", "نکات کلیدی", "بازخوانی", "گفتگو", "مصاحبه", "پوستر", "صوت کامل"
]

def clean_and_audit_corpus():
    print("[*] Starting Full Corpus Audit & Deduplication...")
    
    # Group speeches by date and normalized title
    records_by_date = defaultdict(list)
    
    for year_dir in DATA_DIR.iterdir():
        if not year_dir.is_dir():
            continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue
            for speech_dir in month_dir.iterdir():
                if not speech_dir.is_dir():
                    continue
                
                meta_file = speech_dir / "metadata.json"
                md_file = speech_dir / "content.md"
                
                if meta_file.exists() and md_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        with open(md_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        # Word count & title check
                        word_count = meta.get("word_count", len(content.split()))
                        title = meta.get("title", "")
                        solar_date = meta.get("solar_date", "")
                        
                        records_by_date[solar_date].append({
                            "id": meta["id"],
                            "dir": speech_dir,
                            "title": title,
                            "word_count": word_count,
                            "char_count": meta.get("char_count", len(content)),
                            "has_pdf": meta.get("has_pdf", False),
                            "is_analysis": any(kw in title for kw in ANALYSIS_KEYWORDS)
                        })
                    except Exception as e:
                        pass

    removed_count = 0
    kept_count = 0
    
    for solar_date, items in records_by_date.items():
        if len(items) == 1:
            kept_count += 1
            continue
            
        # Sort items: non-analysis first, highest word_count, has_pdf priority
        items.sort(key=lambda x: (not x["is_analysis"], x["has_pdf"], x["word_count"]), reverse=True)
        
        # Keep the top comprehensive full speech
        primary = items[0]
        kept_count += 1
        
        # Remove truncated excerpts / highlights / duplicate summaries
        for duplicate in items[1:]:
            # If the secondary item is significantly shorter (excerpt) or marked analysis
            if duplicate["word_count"] < primary["word_count"] * 0.7 or duplicate["is_analysis"]:
                try:
                    # Remove duplicate directory
                    for f in duplicate["dir"].iterdir():
                        f.unlink()
                    duplicate["dir"].rmdir()
                    removed_count += 1
                except Exception as e:
                    pass

    print(f"[+] Audit Finished! Kept Complete Speeches: {kept_count}, Removed Excerpts/Duplicates: {removed_count}")

    # Rebuild scraping_progress.json
    existing_ids = set()
    for year_dir in DATA_DIR.iterdir():
        if not year_dir.is_dir(): continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir(): continue
            for speech_dir in month_dir.iterdir():
                if not speech_dir.is_dir(): continue
                meta_file = speech_dir / "metadata.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            m = json.load(f)
                            existing_ids.add(m["id"])
                    except Exception:
                        pass
                        
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(existing_ids), f)
    print(f"[+] Updated progress file with {len(existing_ids)} verified full speeches.")

if __name__ == "__main__":
    clean_and_audit_corpus()
