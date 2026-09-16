# -*- coding: utf-8 -*-
import sys
import json
import sqlite3
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from hazm import Normalizer

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
EXPORTS_DIR = BASE_DIR / "exports"
DB_FILE = DATABASE_DIR / "speeches.db"
JSONL_FILE = EXPORTS_DIR / "speeches_corpus.jsonl"
PARQUET_FILE = EXPORTS_DIR / "speeches_dataset.parquet"

normalizer = Normalizer()

def init_database():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Main table
    c.execute('''
        CREATE TABLE IF NOT EXISTS speeches (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            solar_date TEXT,
            title TEXT,
            normalized_title TEXT,
            url TEXT,
            pdf_url TEXT,
            has_pdf BOOLEAN,
            word_count INTEGER,
            char_count INTEGER,
            content TEXT,
            normalized_content TEXT
        )
    ''')
    
    # FTS5 Full-Text Search Virtual Table
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS speeches_fts USING fts5(
            id UNINDEXED,
            title,
            content,
            normalized_content,
            solar_date
        )
    ''')
    
    conn.commit()
    return conn

def process_and_index_corpus():
    print("[*] Initializing Database...")
    conn = init_database()
    c = conn.cursor()
    
    records = []
    meta_files = list(DATA_DIR.rglob("metadata.json"))
    print(f"[*] Found {len(meta_files)} speech directories to process.")
    
    for meta_path in tqdm(meta_files, desc="Normalizing & Indexing"):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                
            speech_dir = meta_path.parent
            md_path = speech_dir / "content.md"
            
            content = ""
            if md_path.exists():
                with open(md_path, "r", encoding="utf-8") as f_md:
                    content = f_md.read()
                    
            # Normalize with Hazm
            norm_title = normalizer.normalize(meta.get("title", ""))
            norm_content = normalizer.normalize(content)
            
            record = {
                "id": meta["id"],
                "year": meta["year"],
                "month": meta["month"],
                "day": meta["day"],
                "solar_date": meta["solar_date"],
                "title": meta.get("title", ""),
                "normalized_title": norm_title,
                "url": meta.get("url", ""),
                "pdf_url": meta.get("pdf_url"),
                "has_pdf": meta.get("has_pdf", False),
                "word_count": len(content.split()),
                "char_count": len(content),
                "content": content,
                "normalized_content": norm_content
            }
            records.append(record)
            
            # Upsert into SQLite
            c.execute('''
                INSERT OR REPLACE INTO speeches 
                (id, year, month, day, solar_date, title, normalized_title, url, pdf_url, has_pdf, word_count, char_count, content, normalized_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record["id"], record["year"], record["month"], record["day"], record["solar_date"],
                record["title"], record["normalized_title"], record["url"], record["pdf_url"],
                record["has_pdf"], record["word_count"], record["char_count"], record["content"],
                record["normalized_content"]
            ))
            
            # Upsert into FTS5
            c.execute('DELETE FROM speeches_fts WHERE id = ?', (record["id"],))
            c.execute('''
                INSERT INTO speeches_fts (id, title, content, normalized_content, solar_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (record["id"], record["title"], record["content"], record["normalized_content"], record["solar_date"]))
            
        except Exception as e:
            print(f"[!] Error processing {meta_path}: {e}")
            
    conn.commit()
    conn.close()
    print(f"[+] Database successfully populated at {DB_FILE}")
    
    # Export to JSONL & Parquet
    if records:
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        print("[*] Exporting to JSONL & Parquet...")
        df = pd.DataFrame(records)
        df.to_json(JSONL_FILE, orient="records", lines=True, force_ascii=False)
        df.to_parquet(PARQUET_FILE, index=False)
        print(f"[+] JSONL exported to {JSONL_FILE}")
        print(f"[+] Parquet exported to {PARQUET_FILE}")

if __name__ == "__main__":
    process_and_index_corpus()
