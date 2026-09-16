# 🇬🇧 Khamenei Speeches Scraping, Auditing & Ingestion Suite
### Production-Ready Python Data Pipeline with TLS Fingerprinting, WAF Bypass, and Full-Text Quality Auditing

---

## 📌 Technical Summary
This repository houses the end-to-end Python pipeline built to autonomously discover, bypass anti-scraping firewalls, ingest, audit, and export the complete 47-year corpus of official speeches. The architecture adheres to production data engineering principles: idempotency, fault tolerance, and deterministic auditing.

---

## 🧩 Core Architecture Components (`src/`)

### 1. `speech_crawler.py` (Discovery Engine)
- Traverses historical archival endpoints spanning 1357 through 1404 SH.
- Parses pagination, extracts speech identifiers, dates, titles, and persists discovery state to `speech_index.json`.

### 2. `download_worker.py` (Resilient Transport Engine)
- Employs `curl_cffi` to mimic real Google Chrome TLS fingerprints, defeating Cloudflare/WAF bot mitigations without headless browser overhead.
- Downloads sanitized Markdown transcripts, original HTML source snapshots, and publication PDFs.

### 3. `dedup_audit.py` (Transcript Integrity Auditor)
- Implements deterministic filtering heuristics: flags and excludes news briefs, editorial summaries, and analytical op-eds.
- Resolves daily conflicts by scoring transcripts via token volume and official publication proof.

### 4. `export_github_dataset.py` (Analytics Exporter)
- Ingests verified directories and outputs columnar Snappy Parquet, streamable JSONL, and SQLite databases indexed via FTS5.

### 5. `sync_worker.py` (Continuous Pipeline Orchestrator)
- Manages sequential pipeline stages with incremental checkpoints.

---

## 🚀 Usage Guide
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run incremental scraping & verification
python src/sync_worker.py

# 3. Compile output artifacts
python src/export_github_dataset.py
```
