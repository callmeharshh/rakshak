"""
Bulletin agent.

Polls incidents that just became `status = 'dispatched'` (auto-confirmed or
human-approved) and haven't been messaged yet, asks the LLM to draft a short status
update directly in the incident's language (Hindi or Marathi -- one call does both
drafting and translation, not two), and sends it for real over Telegram (Twilio's
trial account had no WhatsApp sending capability -- see agents/bulletin/README.md).
Logs the send to `activity_log`.

Run once:        python3 agents/bulletin/main.py
Limit (testing): python3 agents/bulletin/main.py --limit 1
Poll loop:       python3 agents/bulletin/main.py --loop
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import sb_request, groq_chat, log_activity  # noqa: E402

LANG_NAME = {"hi": "Hinglish (Hindi-English code-mixed, Roman script, no Devanagari)",
             "mr": "Marathi-English code-mixed (Roman script, no Devanagari)"}

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def draft_message(incident):
    lang = LANG_NAME.get(incident["language"], LANG_NAME["hi"])
    prompt = (
        f"Write a short, reassuring status update (under 40 words) in {lang}, for residents of "
        f"{incident['ward']} about this report: \"{incident['description']}\". "
        "A response team has just been dispatched to help. Plain text only, no markdown, no preamble, "
        "Roman/English letters only -- no Devanagari script."
    )
    return groq_chat(prompt, max_tokens=200).strip()


def send_whatsapp(message, chat_id):
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        method="POST", data=body,
    )
    result = json.loads(urllib.request.urlopen(req).read())
    return {"sid": result["result"]["message_id"]}


def process_once(limit=None):
    dispatched = sb_request("incidents?status=eq.dispatched&select=*")
    if not dispatched:
        print("no dispatched incidents")
        return
    sent_log = sb_request("activity_log?agent_name=eq.bulletin&select=incident_id")
    sent_ids = {row["incident_id"] for row in sent_log}

    sent_count = 0
    for inc in dispatched:
        if inc["id"] in sent_ids:
            continue
        if limit is not None and sent_count >= limit:
            break
        message = draft_message(inc)
        chat_id = inc.get("reporter_chat_id") or TELEGRAM_CHAT_ID
        result = send_whatsapp(message, chat_id)
        log_activity("bulletin", inc["id"], "sent_whatsapp", f"sid={result.get('sid', '?')}: {message}")
        print(f"#{inc['id']}: sent -> {message}")
        sent_count += 1


if __name__ == "__main__":
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    if "--loop" in sys.argv:
        while True:
            process_once(limit)
            time.sleep(10)
    else:
        process_once(limit)
