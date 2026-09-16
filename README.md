# ⚙️ Ayatollah Khamenei Speeches Pipeline & Scraping Engine
### Production-Grade Crawling, WAF / CDN Bypass, Deduplication Auditing & Dataset Generation Suite

[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![WAF: Chrome_Bypass](https://img.shields.io/badge/WAF_Bypass-curl__cffi-brightgreen.svg)](https://github.com/mostafao-alavi/khamenei-speeches-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 🌐 Project Ecosystem / اکوسیستم مخازن سه‌گانه
| Repository | Role | Content | Link |
| :--- | :--- | :--- | :--- |
| 📂 **`khamenei-speeches-data`** | **Primary Source Archive** | آرشیو درختی متن کامل سخنرانی‌ها به تفکیک سال و ماه (Markdown, JSON, HTML, PDF) | [GitHub](https://github.com/mostafao-alavi/khamenei-speeches-data) |
| 📊 **`khamenei-speeches-datasets`** | **AI & Analytics Datasets** | دیتاست‌های تجمیعی هوش مصنوعی (Parquet, JSONL, SQLite FTS5) برای RAG و LLM | [GitHub](https://github.com/mostafao-alavi/khamenei-speeches-datasets) |
| ⚙️ **`khamenei-speeches-tools`** | **Engineering & Crawler** | موتور دانلودر ضد مسدودی، ممیزی داده‌ها، و خط لوله استخراج و پاکسازی | [GitHub](https://github.com/mostafao-alavi/khamenei-speeches-tools) |

---

## 🌍 Complete Multilingual Documentation / مستندات کامل چندزبانه
برای مشاهده راهنمای مهندسی به سایر زبان‌ها، پیوندهای زیر را ببینید:
- 🇮🇷 **[فارسی (Persian)](docs/README.fa.md)** - مستندات کامل معماری و اجرای ابزارها
- 🇬🇧 **[English (Default)](docs/README.en.md)** - Full Engineering & Pipeline Documentation
- 🇸🇦 **[العربية (Arabic)](docs/README.ar.md)** - التوثيق الهندسي لأدوات الاستخراج
- 🇨🇳 **[中文 (Chinese)](docs/README.zh.md)** - 爬虫引擎与数据处理工具链技术文档
- 🇫🇷 **[Français (French)](docs/README.fr.md)** - Documentation Technique du Pipeline de Collecte
- 🇹🇷 **[Türkçe (Turkish)](docs/README.tr.md)** - Kazıma Motoru ve Veri Boru Hattı Kılavuzu
- 🇷🇺 **[Русский (Russian)](docs/README.ru.md)** - Техническая Документация Пайплайна Сбора Данных

---

## 🛠️ Architecture & Pipeline Overview

```text
[farsi.khamenei.ir]
        │
        ▼ (Chrome TLS Impersonation / WAF Bypass)
[speech_crawler.py] ──> Discovers 2,291 entries across 1357–1404
        │
        ▼ (Parallel Async / Session Jitter)
[download_worker.py] ──> Saves Markdown, JSON metadata, HTML & PDFs
        │
        ▼ (Full-Transcript Strict Auditor)
[dedup_audit.py] ────> Filters summaries, excerpts, and analyses (yields 1,066 full texts)
        │
        ▼ (Multi-Format Exporter)
[export_github_dataset.py] ──> Generates Parquet, JSONL, and SQLite FTS5
```

### Installation
```bash
git clone https://github.com/mostafao-alavi/khamenei-speeches-tools.git
cd khamenei-speeches-tools
pip install -r requirements.txt
```
