import time
import schedule
import pandas as pd
from datetime import datetime, timezone

from config import ENGLISH_KEYWORDS, TELEGRAM_CHAT_ID, FETCH_ENGLISH, CSV_OUTPUT_PATH
from fetch_news import fetch_news_simple
from dedup import deduplicate_articles
from utils import get_last_published_time
from telegram import send_message  # Adjust import path as needed


def filter_articles_today(articles):
    """Keep only articles published on the current UTC date."""
    today = datetime.now(timezone.utc).date()
    filtered = []
    for a in articles:
        try:
            pub_date = pd.to_datetime(a.get("publishedAt", ""), errors="coerce", utc=True)
            if pub_date.date() == today:
                filtered.append(a)
        except Exception:
            pass
    return filtered


def run():
    last_time = get_last_published_time()
    from_date = last_time.isoformat() if last_time else None
    all_news = []

    if FETCH_ENGLISH:
        # Fetch API news per keyword
        for kw in ENGLISH_KEYWORDS:
            news = fetch_news_simple(kw, lang="en", from_date=from_date)
            if last_time:
                news = [n for n in news if pd.to_datetime(n.get("publishedAt", ""), errors="coerce") > last_time]
            all_news.extend(news)
            time.sleep(1)

        # Fetch RSS news once
        rss_news = fetch_news_simple(keyword=None)
        if last_time:
            rss_news = [n for n in rss_news if pd.to_datetime(n.get("publishedAt", ""), errors="coerce") > last_time]
        all_news.extend(rss_news)

    unique_news = deduplicate_articles(all_news)

    if unique_news:
        # Load existing CSV
        try:
            df = pd.read_csv(CSV_OUTPUT_PATH, encoding='utf-8-sig')
            if 'sent_to_telegram' not in df.columns:
                df['sent_to_telegram'] = False
        except FileNotFoundError:
            # No CSV exists yet
            df = pd.DataFrame(columns=["title", "url", "summary", "publishedAt", "sent_to_telegram"])

        # Convert unique_news list to DataFrame
        df_new = pd.DataFrame(unique_news)
        if 'sent_to_telegram' not in df_new.columns:
            df_new['sent_to_telegram'] = False

        # Combine old and new, dropping duplicates but preserving 'sent_to_telegram' = True
        combined = pd.concat([df, df_new], ignore_index=True)
        combined.sort_values(by=['sent_to_telegram', 'publishedAt'], ascending=[True, True], inplace=True)
        combined = combined.drop_duplicates(subset=['title', 'url'], keep='last')
        combined.reset_index(drop=True, inplace=True)

        # Filter for unsent articles to send to Telegram
        to_send = combined[combined['sent_to_telegram'] == False]

        if to_send.empty:
            print("No new articles to send.")
        else:
            for idx, art in to_send.iterrows():
                send_message(
                    TELEGRAM_CHAT_ID,
                    art.get("title", ""),
                    art.get("summary", ""),
                    art.get("url", "")
                )
                combined.at[idx, 'sent_to_telegram'] = True
                time.sleep(5)

        # Save updated CSV including sent flags
        combined.to_csv(CSV_OUTPUT_PATH, index=False, encoding='utf-8-sig')
        print(f"✅ CSV updated with sent status and saved at {CSV_OUTPUT_PATH}")
    else:
        print("No new articles fetched.")

# Schedule the run every 30 minutes
schedule.every(30).minutes.do(run)

if __name__ == "__main__":
    run()  # run immediately at start
    while True:
        schedule.run_pending()
        time.sleep(10)
