import requests

BOT_TOKEN = "8742109924:AAEGnlvIoPggmp9pTDXv_fhJewg6EotL-rc"
CHAT_ID = "7741970202"


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print("[TELEGRAM] status:", response.status_code)
        print("[TELEGRAM] response:", response.text)
    except Exception as e:
        print("[TELEGRAM ERROR]", str(e))
