# 🇫🇷 Pipeline et Outils de Collecte des Discours de l'Ayatollah Khamenei
### Suite Logicielle Python pour le Contournement de WAF, l'Audit d'Intégrité et l'Exportation de Données

---

## 📌 Résumé Technique
Ce dépôt rassemble les modules Python conçus pour l'exploration, l'acquisition résiliente face aux pare-feux (WAF), l'audit qualité et l'exportation des discours officiels sur 47 ans.

---

## 🧩 Modules Clés (`src/`)
- `speech_crawler.py` : Exploration et cartographie des archives de 1979 à 2026.
- `download_worker.py` : Client HTTP robuste utilisant l'usurpation d'empreinte TLS Chrome via `curl_cffi`.
- `dedup_audit.py` : Filtre algorithmique éliminant les résumés et conservant exclusivement les versions intégrales.
- `export_github_dataset.py` : Génération des jeux de données Parquet, JSONL et base SQLite FTS5.
