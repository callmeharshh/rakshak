"""
Telegram intake agent -- the "wow" feature: anyone can message @RakshakBulletinBot
with a plain-text incident report and watch Sentinel -> Dispatch -> Bulletin process
it live on the dashboard, then get a real reply back on their own phone once help
is dispatched (bulletin/main.py replies to `reporter_chat_id` when it's set).

Long-polls Telegram's getUpdates. Ward is assigned round-robin across a fixed list
of Mumbai wards (shortcut: no geocoding of free text, good enough for a live demo).

Run: python3 agents/intake_telegram.py
"""
import itertools
import json
import os
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import sb_request, log_activity, WARDS  # noqa: E402

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API = f"https://api.telegram.org/bot{TOKEN}"
DASHBOARD_URL = "https://rakshak-ps03-smoothoperator.netlify.app"

ward_cycle = itertools.cycle(WARDS.items())


def send(chat_id, text):
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    urllib.request.urlopen(urllib.request.Request(f"{API}/sendMessage", method="POST", data=body))


def get_updates(offset):
    url = f"{API}/getUpdates?timeout=30&offset={offset}"
    return json.loads(urllib.request.urlopen(url, timeout=35).read())["result"]


def handle(update):
    msg = update.get("message")
    if not msg or "text" not in msg:
        return
    chat_id = msg["chat"]["id"]
    text = msg["text"].strip()
    if text.startswith("/start"):
        send(chat_id, "Send me a one-line disaster report (e.g. \"Waterlogging near Kurla, family stranded\") "
                       "and RAKSHAK's agents will triage and dispatch help -- watch it live at " + DASHBOARD_URL)
        return

    ward, (lat, lon, lang) = next(ward_cycle)
    inc = sb_request("incidents", "POST", {
        "source": "telegram_live", "ward": ward, "lat": lat, "lon": lon,
        "description": text, "need_type": "rescue", "language": lang,
        "status": "new", "reporter_chat_id": chat_id,
    }, return_repr=True)
    send(chat_id, f"Got it -- logged as an incident in {ward}. RAKSHAK's agents are triaging it now. "
                   f"Watch live: {DASHBOARD_URL}\nYou'll get another message here once help is dispatched.")
    if inc:
        log_activity("intake", inc[0]["id"], "reported_via_telegram", f"chat_id={chat_id}: {text}")


def main():
    offset = 0
    print("Telegram intake listening for messages to @RakshakBulletinBot...")
    while True:
        for update in get_updates(offset):
            offset = update["update_id"] + 1
            try:
                handle(update)
            except Exception as e:
                print(f"error handling update: {e}")


if __name__ == "__main__":
    main()
