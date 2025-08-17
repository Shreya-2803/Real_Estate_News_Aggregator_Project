import requests
import re
import time
from config import TELEGRAM_BOT_TOKEN

def escape_markdown(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r'([\\_*[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def format_message(title: str, summary: str, url: str) -> str:
    title_esc = escape_markdown(title or "No Title")
    summary_esc = escape_markdown(summary or "")
    url_esc = url or ""
    msg = f"*{title_esc}*\n\n"
    if summary_esc:
        msg += f"{summary_esc}\n\n"
    if url_esc:
        msg += f"[Read more]({url_esc})"
    return msg[:4000]

def send_message(chat_id: str, title: str, summary: str, url: str):
    message = format_message(title, summary, url)
    url_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": False
    }

    max_retries = 5
    backoff = 1  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(url_api, json=payload, timeout=60)
            if r.status_code == 200:
                print(f"✅ Sent: {title}")
                return
            else:
                print(f"[❌ ERROR {r.status_code}] {r.text}")
                return
        except requests.exceptions.Timeout:
            print(f"[❌ Timeout error] Attempt {attempt}: Sending message timed out: {title}")
        except Exception as e:
            print(f"[❌ Exception] Attempt {attempt}: Telegram send failed: {e}")

        if attempt < max_retries:
            time.sleep(backoff)
            backoff *= 2  # exponential backoff

    print(f"[❌ Failed] All {max_retries} attempts to send message timed out or failed: {title}")
