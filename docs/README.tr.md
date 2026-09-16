# 🇹🇷 Ayetullah Hamaney Konuşmaları Veri Kazıma ve Boru Hattı Araçları
### TLS Parmak İzi, WAF Atlama, Tam Metin Denetimi ve Veri Kümesi Üretim Paketi

---

## 📌 Genel Bakış
Bu depo, 47 yıllık konuşma arşivini internet üzerinden toplamak, güvenlik duvarlarını aşmak, metin bütünlüğünü doğrulamak ve veri kümelerini üretmek için geliştirilen Python araçlarını içerir.

---

## 🧩 Temel Bileşenler (`src/`)
- `speech_crawler.py`: 1979-2026 yılları arasındaki konuşma dizinlerini tarayan araç.
- `download_worker.py`: TLS taklidiyle Cloudflare ve WAF engellerini aşan indirme modülü.
- `dedup_audit.py`: Özetleri eleyip yalnızca tam metinleri seçen denetim motoru.
- `export_github_dataset.py`: Parquet, JSONL ve SQLite veri kümelerini oluşturan modül.
