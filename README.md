# Real_Estate_News_Aggregator_Project
This project is a domain-specific news aggregation system that collects and organizes the latest updates from Real Estate, Real Estate Legal, and Healthcare sectors. It integrates multiple APIs (GNews, NewsAPI, Mediastack) and RSS feeds from trusted sources to ensure timely and relevant coverage.

🚀 Features

Aggregates news from APIs + RSS feeds

Domain-specific keyword filtering (Real Estate, Legal, Healthcare)

Deduplication with similarity checks

CSV export with OneDrive cloud backup

Automated Telegram alerts for fresh news

Multilingual-ready (currently supports English)

🛠️ Tech Stack

Python (requests, pandas, feedparser, datetime)

APIs: GNews, NewsAPI, Mediastack

Storage: CSV + OneDrive backup

Notifications: Telegram Bot API

📂 Project Structure

config.py → Centralized configuration (API keys, feeds, keywords)

fetch_news.py → Fetch & filter fresh domain-specific news

save_to_csv.py → Persist, deduplicate & back up data

send_to_telegram.py → Push updates to Telegram channel
