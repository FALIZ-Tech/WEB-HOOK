import requests
from config import ACCESS_TOKEN, PHONE_NUMBER_ID

def send_whatsapp_message(recipient: str, text: str) -> bool:
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("[WA] Missing credentials")
        return False

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": text[:4096]}
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code == 200:
            print(f"[WA] Sent to {recipient}")
            return True
        print(f"[WA] Send failed {r.status_code}: {r.text}")
        return False
    except Exception as e:
        print(f"[WA] Network error: {e}")
        return False

def parse_incoming_whatsapp(data: dict) -> list:
    results = []
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    if msg.get("type") == "text":
                        phone = msg.get("from")
                        body = msg.get("text", {}).get("body", "").strip()
                        if phone and body:
                            results.append((phone, body))
    except Exception as e:
        print(f"[WA] Parse error: {e}")
    return results
