import schedule
import time
import subprocess
import sys
import os
from datetime import datetime

LOG_FILE = "scheduler_log.txt"

def log(message: str):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    print(log_entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as logf:
            logf.write(log_entry + "\n")
    except Exception as e:
        print(f"[LOGGING ERROR] Failed to write log: {e}")

def job():
    log("🕑 Running scheduled message delivery...")

    try:
        # Get absolute path relative to this script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, "main.py")

        result = subprocess.run(
            [sys.executable, main_script],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            log(f"[❌ ERROR] main.py failed with return code {result.returncode}:\n{result.stderr.strip()}")
        else:
            log("✅ main.py executed successfully.")
            if result.stdout.strip():
                log(f"[OUTPUT] {result.stdout.strip()}")
    except subprocess.TimeoutExpired:
        log("[❌ ERROR] main.py execution timed out.")
    except Exception as e:
        log(f"[❌ EXCEPTION] {e}")

def main():
    log("📅 Scheduler started. Waiting for next job...")

    schedule.every(30).minutes.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(10)  # Check every 10 seconds
    except KeyboardInterrupt:
        log("🛑 Scheduler stopped by user.")

if __name__ == "__main__":
    main()
