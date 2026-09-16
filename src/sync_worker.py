# -*- coding: utf-8 -*-
import sys
import json
import time
import os
from pathlib import Path
import incremental_crawler
import downloader
import processor

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
STATUS_FILE = LOGS_DIR / "sync_status.json"

def sync_cycle():
    print("="*60)
    print(f"[*] Starting Sync & Discover Cycle at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. Crawl any missing years / new updates
    try:
        total_indexed = incremental_crawler.crawl_missing_years()
    except Exception as e:
        print(f"[!] Crawler error: {e}")
        total_indexed = 0

    # 2. Download pending speeches and PDFs
    try:
        downloader.download_all_speeches(max_workers=5, download_pdf=True)
    except Exception as e:
        print(f"[!] Downloader error: {e}")

    # 3. Update Database and Exports
    try:
        processor.process_and_index_corpus()
    except Exception as e:
        print(f"[!] Processor error: {e}")

    # Save summary status
    completed_ids = downloader.load_progress()
    status = {
        "last_sync": time.time(),
        "last_sync_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_indexed": total_indexed,
        "total_downloaded": len(completed_ids)
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
        
    print(f"[+] Sync Cycle Completed. Total Downloaded: {len(completed_ids)}")

if __name__ == "__main__":
    sync_cycle()
