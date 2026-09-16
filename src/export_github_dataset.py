# -*- coding: utf-8 -*-
"""
Khamenei Speeches Corpus - Dataset Architecture & Export Pipeline
Designed for LLMs, RAG systems, and AI research.
"""
import os
import json
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
EXPORTS_DIR = BASE_DIR / "exports"

def build_github_ready_dataset():
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    
    records = []
    print("[*] Collecting all validated speeches for GitHub & RAG export...")
    
    for year_dir in sorted(DATA_DIR.iterdir()):
        if not year_dir.is_dir(): continue
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir(): continue
            for speech_dir in sorted(month_dir.iterdir()):
                if not speech_dir.is_dir(): continue
                
                meta_file = speech_dir / "metadata.json"
                md_file = speech_dir / "content.md"
                pdf_file = speech_dir / "document.pdf"
                
                if meta_file.exists() and md_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        with open(md_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        # Extract clean speech body
                        body = content.split("---", 1)[-1].strip() if "---" in content else content
                        
                        records.append({
                            "id": meta["id"],
                            "year": meta["year"],
                            "solar_date": meta.get("solar_date", ""),
                            "title": meta.get("title", ""),
                            "url": meta.get("url", ""),
                            "has_pdf": pdf_file.exists() or meta.get("has_pdf", False),
                            "word_count": len(body.split()),
                            "char_count": len(body),
                            "content": body
                        })
                    except Exception as e:
                        pass

    print(f"[+] Total Speeches Prepared: {len(records)}")
    
    # 1. Export JSONL (Optimized for RAG & Fine-tuning)
    jsonl_path = EXPORTS_DIR / "khamenei_speeches_corpus.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[+] JSONL generated at {jsonl_path}")
    
    # 2. Export Parquet (High performance for Pandas, Polars, DuckDB)
    df = pd.DataFrame(records)
    parquet_path = EXPORTS_DIR / "khamenei_speeches_corpus.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"[+] Parquet generated at {parquet_path}")

    # 3. Export SQLite with FTS5 Full-Text Search
    db_path = DATABASE_DIR / "speeches_fts.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS speeches")
    cur.execute("""
        CREATE TABLE speeches (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            solar_date TEXT,
            title TEXT,
            url TEXT,
            has_pdf INTEGER,
            word_count INTEGER,
            char_count INTEGER,
            content TEXT
        )
    """)
    cur.execute("DROP TABLE IF EXISTS speeches_fts")
    cur.execute("CREATE VIRTUAL TABLE speeches_fts USING fts5(title, content, tokenize='unicode61')")
    
    for r in records:
        cur.execute("""
            INSERT INTO speeches (id, year, solar_date, title, url, has_pdf, word_count, char_count, content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (r["id"], r["year"], r["solar_date"], r["title"], r["url"], int(r["has_pdf"]), r["word_count"], r["char_count"], r["content"]))
        cur.execute("INSERT INTO speeches_fts (title, content) VALUES (?, ?)", (r["title"], r["content"]))
        
    conn.commit()
    conn.close()
    print(f"[+] SQLite FTS5 Database generated at {db_path}")

if __name__ == "__main__":
    build_github_ready_dataset()
