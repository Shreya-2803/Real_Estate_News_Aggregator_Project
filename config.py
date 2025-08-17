from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file environment variables

# Load environment variables once
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY")
NEWS_API = os.getenv("NEWS_API")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ONEDRIVE_FOLDER = os.getenv("ONEDRIVE_FOLDER")

# Validate all required environment variables
REQUIRED_ENV_VARS = {
    "GNEWS_API_KEY": GNEWS_API_KEY,
    "MEDIASTACK_API_KEY": MEDIASTACK_API_KEY,
    "NEWS_API": NEWS_API,
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    "ONEDRIVE_FOLDER": ONEDRIVE_FOLDER,
}

missing_vars = [key for key, val in REQUIRED_ENV_VARS.items() if not val]
if missing_vars:
    raise EnvironmentError(f"❌ Missing required environment variables: {', '.join(missing_vars)}")

# Configuration constants
LANGUAGES = {"en": "English"}
ENGLISH_KEYWORDS = [
    "India real estate",
    "India property market",
    "India housing sector",
    "India real estate prices",
    "India residential projects",
    "India new housing projects",
    "India affordable housing",
    "India real estate investment",
    "India property rates",

]

RSS_FEEDS = [
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://www.telegraphindia.com/feeds/rss.jsp?id=3",
    "https://www.thestatesman.com/feed",
    "https://indianexpress.com/section/india/feed/",
    # ... add more as needed
]


MAX_RESULTS_PER_KEYWORD = 10
FETCH_ENGLISH = True

CSV_OUTPUT_PATH = os.path.join(ONEDRIVE_FOLDER, "real_estate_kolkata.csv")

SIMILARITY_THRESHOLD = 0.75
MERGE_DUPLICATE_URLS = True
