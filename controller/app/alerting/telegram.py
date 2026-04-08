import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[TELEGRAM] missing config")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=5)

        print(f"[TELEGRAM] status: {response.status_code}")
        print(f"[TELEGRAM] response: {response.text}")

    except Exception as e:
        print(f"[TELEGRAM] error: {e}")
