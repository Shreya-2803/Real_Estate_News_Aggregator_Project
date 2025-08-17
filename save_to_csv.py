import pandas as pd
import os
import json
from config import CSV_OUTPUT_PATH, ONEDRIVE_FOLDER


def save_to_csv(data, path=CSV_OUTPUT_PATH):
    if not data:
        print("⚠️ No data to save.")
        return

    if not path or not isinstance(path, str):
        print("[ERROR] Invalid or missing CSV path.")
        return

    dir_path = os.path.dirname(path)
    if dir_path:  # Avoid error if path is filename only
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            print(f"[ERROR] Could not create output directory '{dir_path}': {e}")
            return

    try:
        df_new = pd.DataFrame(data)
        if df_new.empty:
            print("⚠️ DataFrame is empty; skipping CSV save.")
            return
    except Exception as e:
        print(f"[ERROR] Failed to convert data to DataFrame: {e}")
        return

    # Normalize 'publishedAt' column if present
    if 'publishedAt' in df_new.columns:
        df_new['publishedAt'] = pd.to_datetime(df_new['publishedAt'], errors='coerce', utc=True)

    # Add 'sent_to_telegram' column if missing, default to False
    if 'sent_to_telegram' not in df_new.columns:
        df_new['sent_to_telegram'] = False

    # Convert list columns like 'urls' to JSON-ready strings
    for col in ['urls']:
        if col in df_new.columns:
            df_new[col] = df_new[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

    try:
        if os.path.exists(path):
            existing_df = pd.read_csv(path, encoding='utf-8-sig', dtype=str)
            if 'publishedAt' in existing_df.columns:
                existing_df['publishedAt'] = pd.to_datetime(existing_df['publishedAt'], errors='coerce', utc=True)

            # Add 'sent_to_telegram' column to existing_df if missing
            if 'sent_to_telegram' not in existing_df.columns:
                existing_df['sent_to_telegram'] = False

            # Combine old and new data
            combined_df = pd.concat([existing_df, df_new], ignore_index=True)

            # Drop duplicates by title & url, but keep the row with sent_to_telegram=True if duplicates exist
            combined_df.sort_values(by=['sent_to_telegram', 'publishedAt'], ascending=[False, True], inplace=True)
            combined_df = combined_df.drop_duplicates(subset=['title', 'url'], keep='first')

            # Sort by publishedAt ascending
            if 'publishedAt' in combined_df.columns:
                combined_df = combined_df.sort_values('publishedAt', ascending=True).reset_index(drop=True)
        else:
            combined_df = df_new
            if 'publishedAt' in combined_df.columns:
                combined_df = combined_df.sort_values('publishedAt', ascending=True).reset_index(drop=True)

        combined_df.to_csv(path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV saved to: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to save CSV to {path}: {e}")
        return

    # Optional OneDrive backup
    if ONEDRIVE_FOLDER:
        try:
            filename = os.path.basename(path)
            onedrive_path = os.path.join(ONEDRIVE_FOLDER, filename)
            combined_df.to_csv(onedrive_path, index=False, encoding='utf-8-sig')
            print(f"☁️ CSV also saved to OneDrive: {onedrive_path}")
        except Exception as e:
            print(f"[ERROR] Failed to sync with OneDrive: {e}")
