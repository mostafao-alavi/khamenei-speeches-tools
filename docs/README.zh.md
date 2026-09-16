# 🇨🇳 阿亚图拉·哈梅内伊演讲数据抓取、审计与流水线引擎
### 基于 Python 的工程级爬虫、WAF 防火墙绕过、全文去重审计与数据集生成工具集

---

## 📌 技术架构概述
本仓库包含用于抓取、反爬防御绕过、文本标准化、全文完整性审计以及标准数据集生成的完整 Python 代码库。

---

## 🧩 核心模块说明 (`src/`)
- `speech_crawler.py`: 索引抓取器，负责检索 1979 至 2026 年间的所有演讲目录。
- `download_worker.py`: 基于 `curl_cffi` 的高性能传输引擎，完美模拟 Chrome 浏览器的 TLS 指纹以绕过防火墙封锁。
- `dedup_audit.py`: 全文审计模块，依据词数权重及官方发布凭证，剔除节选与新闻简报。
- `export_github_dataset.py`: 导出工具，将审核后的数据转换为 Parquet、JSONL 与 SQLite FTS5 数据库。
