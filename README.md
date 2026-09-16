# ⚙️ Khamenei Speeches Engine & Scraping Tools
### High-Performance Crawling, WAF Bypass, Deduplication Audit & Pipeline Tools / ابزارها و موتور استخراج، ممیزی و پالایش متون

[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![WAF: Chrome_Bypass](https://img.shields.io/badge/WAF_Bypass-curl__cffi-brightgreen.svg)](https://github.com/mostafao-alavi/khamenei-speeches-tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 🌐 Ecosystem Repositories / ریپازیتوری‌های سه‌گانه پروژه
| Repository | Description | Link |
| :--- | :--- | :--- |
| 📂 **`khamenei-speeches-data`** | آرشیو درختی متن کامل سخنرانی‌ها به تفکیک سال و ماه (Markdown & PDF) | [مشاهده ریپو](https://github.com/mostafao-alavi/khamenei-speeches-data) |
| 📊 **`khamenei-speeches-datasets`** | دیتاست‌های آماده هوش مصنوعی و تحلیل داده (Parquet, JSONL, SQLite FTS5) | [مشاهده ریپو](https://github.com/mostafao-alavi/khamenei-speeches-datasets) |
| ⚙️ **`khamenei-speeches-tools`** | ابزارها و کدهای خزشگر هوشمند، ممیزی، حذف تکراری‌ها و خط لوله استخراج | [مشاهده ریپو](https://github.com/mostafao-alavi/khamenei-speeches-tools) |

---

## 🌍 Multilingual Navigation
- [🇮🇷 فارسی (Persian)](#فارسی)
- [🇬🇧 English](#english)
- [🇸🇦 العربية (Arabic)](#العربية)
- [🇨🇳 中文 (Chinese)](#中文)
- [🇫🇷 Français (French)](#français)
- [🇹🇷 Türkçe (Turkish)](#türkçe)
- [🇷🇺 Русский (Russian)](#русский)

---

<a name="فارسی"></a>
## 🇮🇷 فارسی
### درباره این ابزارها
این مخزن شامل کدهای منبع پایتون، خط لوله دانلود، موتور دور زدن فایروال و سیستم هوشمند ممیزی و حذف داده‌های تکراری و غیرکامل برای استخراج آرشیو بیانات است.

### ساختار اسکریپت‌ها (`src/`)
- `speech_crawler.py`: خزشگر خودکار شاخص سخنرانی‌ها از سال ۱۳۵۷ تا ۱۴۰۴ با پشتیبانی از صف هوشمند.
- `download_worker.py`: دانلودر موازی متون، کدهای HTML و اسناد PDF رسمی با نشست شبیه‌ساز Chrome و پشتیبانی از فایروال/WAF.
- `dedup_audit.py`: موتور ممیزی و غربال‌گری داده‌ها جهت تضمین ذخیره‌سازی **فقط نسخه کامل** و حذف خلاصه‌ها و تحلیل‌ها.
- `export_github_dataset.py`: تولید خودکار فایل‌های Parquet، JSONL و ساخت جدول جستجوی تمام‌متن FTS5 در دیتابیس SQLite.
- `sync_worker.py`: پردازشگر خودکار جهت اجرای ترتیبی و افزایشی کل خط لوله.

### نحوه راه‌اندازی و اجرا
```bash
# نصب پیش‌نیازها
pip install -r requirements.txt

# اجرای همگام‌سازی و دانلود
python src/sync_worker.py

# خروجی‌گیری دیتاست‌ها
python src/export_github_dataset.py
```

---

<a name="english"></a>
## 🇬🇧 English
### Overview
This repository contains the complete modular Python engine and automated pipeline used to scrape, normalize, audit, deduplicate, and export the comprehensive textual archive of Khamenei speeches.

### Pipeline Components
- `speech_crawler.py`: Discovers and indexes speech endpoints from 1979 to 2026.
- `download_worker.py`: Resilient HTTP client powered by `curl_cffi` for TLS fingerprinting and WAF bypass.
- `dedup_audit.py`: Full-text integrity auditor filtering excerpts, news briefs, and editorial analyses.
- `export_github_dataset.py`: Exports datasets into Parquet, JSONL, and SQLite FTS5 databases.

---

<a name="العربية"></a>
## 🇸🇦 العربية
### نظرة عامة
يحتوي هذا المستودع على محرك بايثون المتكامل والأدوات البرمجية المستخدمة في جمع وتدقيق وتصفية الخطابات وتصديرها بصيغ البيانات القياسية.
