# import requests
# import pandas as pd
# from config import GNEWS_API_KEY, NEWS_API, MEDIASTACK_API_KEY, MAX_RESULTS_PER_KEYWORD
#
# def _safe_get_str(d, key1, key2=None):
#     val = d.get(key1) or (d.get(key2) if key2 else "") or ""
#     return val.strip() if isinstance(val, str) else ""
#
# def _is_after_date(published_at_str: str, from_date: str):
#     """
#     Return True if published_at_str > from_date (strictly greater).
#     If either date is missing or invalid, return True to avoid missing news.
#     """
#     if not published_at_str or not from_date:
#         return True  # Keep the article if date info is missing
#
#     try:
#         pub_dt = pd.to_datetime(published_at_str, utc=True)
#         from_dt = pd.to_datetime(from_date, utc=True)
#         return pub_dt > from_dt
#     except Exception:
#         return True  # In case of parsing error, include the article to be safe
#
# def fetch_news_simple(keyword, lang="en", from_date=None):
#     """
#     Fetches news articles only published after from_date from supported APIs.
#     Returns list of dicts with 'title', 'url', 'summary', 'publishedAt' fields.
#     """
#     if lang != "en":
#         print(f"[ℹ️] Skipping non-English keyword: {keyword}")
#         return []
#
#     articles = []
#
#     # 1. GNews API
#     try:
#         params = {
#             "q": keyword,
#             "lang": lang,
#             "max": MAX_RESULTS_PER_KEYWORD,
#             "token": GNEWS_API_KEY,
#         }
#         if from_date:
#             params["from"] = from_date
#
#         r = requests.get("https://gnews.io/api/v4/search", params=params)
#         r.raise_for_status()
#         data = r.json()
#         for item in data.get("articles", []):
#             if len(articles) >= MAX_RESULTS_PER_KEYWORD:
#                 break
#             published_at = _safe_get_str(item, "publishedAt")
#             if not _is_after_date(published_at, from_date):
#                 continue
#             articles.append({
#                 "title": _safe_get_str(item, "title"),
#                 "url": _safe_get_str(item, "url"),
#                 "summary": _safe_get_str(item, "description"),
#                 "publishedAt": published_at,
#             })
#         print(f"[✅ GNews] {len(articles)} articles for: {keyword}")
#     except Exception as e:
#         print(f"[❌ GNews ERROR] {keyword}: {e}")
#
#     # 2. NewsAPI
#     if len(articles) < MAX_RESULTS_PER_KEYWORD:
#         try:
#             params = {
#                 "q": keyword,
#                 "language": lang,
#                 "pageSize": MAX_RESULTS_PER_KEYWORD - len(articles),
#                 "sortBy": "publishedAt",
#                 "apiKey": NEWS_API,
#             }
#             if from_date:
#                 params["from"] = from_date
#
#             r = requests.get("https://newsapi.org/v2/everything", params=params)
#             r.raise_for_status()
#             data = r.json()
#             for item in data.get("articles", []):
#                 if len(articles) >= MAX_RESULTS_PER_KEYWORD:
#                     break
#                 published_at = _safe_get_str(item, "publishedAt")
#                 if not _is_after_date(published_at, from_date):
#                     continue
#                 articles.append({
#                     "title": _safe_get_str(item, "title"),
#                     "url": _safe_get_str(item, "url"),
#                     "summary": _safe_get_str(item, "description"),
#                     "publishedAt": published_at,
#                 })
#             print(f"[✅ NewsAPI] {len(data.get('articles', []))} articles for: {keyword}")
#         except Exception as e:
#             print(f"[❌ NewsAPI ERROR] {keyword}: {e}")
#
#     # 3. Mediastack (fallback)
#     if len(articles) < MAX_RESULTS_PER_KEYWORD:
#         try:
#             params = {
#                 "access_key": MEDIASTACK_API_KEY,
#                 "keywords": keyword,
#                 "languages": lang,
#                 "limit": MAX_RESULTS_PER_KEYWORD - len(articles),
#                 "sort": "published_desc",
#             }
#             if from_date:
#                 # pass only date part for Mediastack API
#                 params["date"] = from_date.split("T")[0]
#
#             r = requests.get("https://api.mediastack.com/v1/news", params=params)
#             r.raise_for_status()
#             data = r.json()
#             for item in data.get("data", []):
#                 if len(articles) >= MAX_RESULTS_PER_KEYWORD:
#                     break
#                 published_at = _safe_get_str(item, "publishedAt", "published_at")
#                 if not _is_after_date(published_at, from_date):
#                     continue
#                 articles.append({
#                     "title": _safe_get_str(item, "title"),
#                     "url": _safe_get_str(item, "url"),
#                     "summary": _safe_get_str(item, "description"),
#                     "publishedAt": published_at,
#                 })
#             print(f"[✅ Mediastack] {len(data.get('data', []))} articles for: {keyword}")
#         except Exception as e:
#             print(f"[❌ Mediastack ERROR] {keyword}: {e}")
#
#     return articles[:MAX_RESULTS_PER_KEYWORD]


import requests
import pandas as pd
import feedparser
from datetime import datetime, timezone
from config import (
    GNEWS_API_KEY,
    NEWS_API,
    MEDIASTACK_API_KEY,
    MAX_RESULTS_PER_KEYWORD,
    RSS_FEEDS,
    ENGLISH_KEYWORDS,
)

def _safe_get_str(d, key1, key2=None):
    val = d.get(key1) or (d.get(key2) if key2 else "") or ""
    return val.strip() if isinstance(val, str) else ""

def _is_today(published_at_str):
    try:
        pub_dt = pd.to_datetime(published_at_str, utc=True)
        return pub_dt.date() == datetime.now(timezone.utc).date()
    except Exception:
        return False

def _matches_keywords(article, keywords):
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    return any(k.lower() in text for k in keywords)

def fetch_news_simple(keyword=None, lang="en", from_date=None):
    articles = []

    # ==== 1. GNews API ====
    if keyword:
        try:
            params = {
                "q": keyword,
                "lang": lang,
                "max": MAX_RESULTS_PER_KEYWORD,
                "token": GNEWS_API_KEY,
            }
            if from_date:
                params["from"] = from_date

            r = requests.get("https://gnews.io/api/v4/search", params=params)
            r.raise_for_status()
            data = r.json()
            for item in data.get("articles", []):
                published_at = _safe_get_str(item, "publishedAt")
                if not _is_today(published_at):
                    continue
                articles.append({
                    "title": _safe_get_str(item, "title"),
                    "url": _safe_get_str(item, "url"),
                    "summary": _safe_get_str(item, "description"),
                    "publishedAt": published_at,
                })
            print(f"[✅ GNews] {len(articles)} today's articles for: {keyword}")
        except Exception as e:
            print(f"[❌ GNews ERROR] {keyword}: {e}")

    # ==== 2. NewsAPI ====
    if keyword and len(articles) < MAX_RESULTS_PER_KEYWORD:
        try:
            params = {
                "q": keyword,
                "language": lang,
                "pageSize": MAX_RESULTS_PER_KEYWORD - len(articles),
                "sortBy": "publishedAt",
                "apiKey": NEWS_API,
            }
            if from_date:
                params["from"] = from_date

            r = requests.get("https://newsapi.org/v2/everything", params=params)
            r.raise_for_status()
            data = r.json()
            for item in data.get("articles", []):
                published_at = _safe_get_str(item, "publishedAt")
                if not _is_today(published_at):
                    continue
                articles.append({
                    "title": _safe_get_str(item, "title"),
                    "url": _safe_get_str(item, "url"),
                    "summary": _safe_get_str(item, "description"),
                    "publishedAt": published_at,
                })
            print(f"[✅ NewsAPI] {len(data.get('articles', []))} fetched, {len([a for a in articles if _is_today(a['publishedAt'])])} today's for: {keyword}")
        except Exception as e:
            print(f"[❌ NewsAPI ERROR] {keyword}: {e}")

    # ==== 3. Mediastack (fallback) ====
    if keyword and len(articles) < MAX_RESULTS_PER_KEYWORD:
        try:
            params = {
                "access_key": MEDIASTACK_API_KEY,
                "keywords": keyword,
                "languages": lang,
                "limit": MAX_RESULTS_PER_KEYWORD - len(articles),
                "sort": "published_desc",
            }
            if from_date:
                params["date"] = from_date.split("T")[0]

            r = requests.get("https://api.mediastack.com/v1/news", params=params)
            r.raise_for_status()
            data = r.json()
            for item in data.get("data", []):
                published_at = _safe_get_str(item, "publishedAt", "published_at")
                if not _is_today(published_at):
                    continue
                articles.append({
                    "title": _safe_get_str(item, "title"),
                    "url": _safe_get_str(item, "url"),
                    "summary": _safe_get_str(item, "description"),
                    "publishedAt": published_at,
                })
            print(f"[✅ Mediastack] {len(data.get('data', []))} fetched, {len([a for a in articles if _is_today(a['publishedAt'])])} today's for: {keyword}")
        except Exception as e:
            print(f"[❌ Mediastack ERROR] {keyword}: {e}")

    # ==== 4. RSS feeds ====
    try:
        for rss_url in RSS_FEEDS:
            feed = feedparser.parse(rss_url)
            feed_source = feed.feed.get("title", rss_url)
            for entry in feed.entries:
                published_at = getattr(entry, "published", None) or entry.get("updated", "")
                if not _is_today(published_at):
                    continue
                article = {
                    "title": entry.get("title"),
                    "url": entry.get("link"),
                    "summary": entry.get("summary", ""),
                    "publishedAt": published_at,
                    "source": feed_source
                }
                # When keyword is None, filter with all ENGLISH_KEYWORDS, else filter with keyword only
                keywords_to_check = [keyword] if keyword else ENGLISH_KEYWORDS
                if matches_keywords(article, keywords_to_check):
                    articles.append(article)
        print(f"[✅ RSS] Total {len(articles)} today's articles matching keywords from RSS feeds")
    except Exception as e:
        print(f"[❌ RSS ERROR] {e}")

    return articles


def matches_keywords(article, keywords):
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    return any(k.lower() in text for k in keywords)


