import pandas as pd
import os
from config import CSV_OUTPUT_PATH
from typing import Optional

def get_last_published_time() -> Optional[pd.Timestamp]:
    """
    Retrieves the latest 'publishedAt' datetime from the CSV file.

    Returns:
        pd.Timestamp or None: Latest publication time if found and valid, else None.
    """
    try:
        if not CSV_OUTPUT_PATH or not isinstance(CSV_OUTPUT_PATH, str) or not CSV_OUTPUT_PATH.endswith(".csv"):
            print("[⚠️] Invalid or missing CSV_OUTPUT_PATH in config.")
            return None

        if not os.path.exists(CSV_OUTPUT_PATH):
            print("[ℹ️] CSV file does not exist yet. No previous records found.")
            return None

        df = pd.read_csv(CSV_OUTPUT_PATH)
        if df.empty or "publishedAt" not in df.columns:
            print("[ℹ️] No 'publishedAt' data in CSV. Nothing to compare.")
            return None

        df["publishedAt"] = pd.to_datetime(df["publishedAt"], errors="coerce", utc=True)

        valid_dates = df["publishedAt"].dropna()
        if valid_dates.empty:
            print("[ℹ️] No valid 'publishedAt' timestamps found.")
            return None

        latest_time = valid_dates.max()
        return latest_time

    except Exception as e:
        print(f"[❌ ERROR] Failed to get last published time: {e}")
        return None
