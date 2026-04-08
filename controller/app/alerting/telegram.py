import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[TELEGRAM] Missing config")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # 🔥 IMPORTANT: remove markdown issues
    safe_message = message.replace("*", "").replace("_", "").replace("`", "")

    payload = {
        "chat_id": CHAT_ID,
        "text": safe_message,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        print("[TELEGRAM] status:", response.status_code)
        print("[TELEGRAM] response:", response.text)

    except Exception as e:
        print("[TELEGRAM ERROR]", str(e))
