"""
Sentinel agent.

Polls `incidents` where status = 'new', asks an LLM for severity (1-5) and need_type,
checks for a nearby open duplicate (same ward, within 500m) via the Haversine formula,
and writes the result back to Supabase plus an activity_log row.

Run once:  python3 agents/sentinel/main.py
Poll loop: python3 agents/sentinel/main.py --loop
"""
import json
import math
import os
import re
import sys
import time
import urllib.request


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    for line in open(env_path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


load_env()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]
GROQ_KEY = os.environ["LLM_API_KEY"]


def sb_request(path, method="GET", body=None):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "return=minimal"
    req = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{path}", method=method, data=data, headers=headers)
    resp = urllib.request.urlopen(req).read()
    return json.loads(resp) if resp else None


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


assert haversine_km(19.0, 72.8, 19.0, 72.8) < 1e-9  # same point -> 0 km, sanity check


def score_with_llm(description):
    prompt = (
        "You triage disaster-response SOS reports for a flood/heatwave response system in India. "
        "Given the report, reply with ONLY compact JSON, nothing else: "
        '{"severity": <1-5 int, 5 = life-threatening>, "need_type": "<rescue|medical|food|shelter|water>"}\n\n'
        f"Report: {description}"
    )
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 300,
        "reasoning_effort": "low",
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", method="POST", data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json", "User-Agent": "rakshak/1.0"},
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    text = resp["choices"][0]["message"]["content"]
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"LLM didn't return JSON: {text!r}")
    data = json.loads(match.group(0))
    return int(data["severity"]), data["need_type"]


def find_duplicate(incident, open_incidents, radius_km=0.5):
    for other in open_incidents:
        if other["id"] == incident["id"] or other["ward"] != incident["ward"]:
            continue
        if haversine_km(incident["lat"], incident["lon"], other["lat"], other["lon"]) <= radius_km:
            return other["id"]
    return None


def log(incident_id, action, details=""):
    sb_request("activity_log", "POST", {"agent_name": "sentinel", "incident_id": incident_id, "action": action, "details": details})


def process_once():
    new_incidents = sb_request("incidents?status=eq.new&select=*")
    if not new_incidents:
        print("no new incidents")
        return
    open_incidents = sb_request("incidents?status=in.(triaged,dispatched)&select=*")

    for inc in new_incidents:
        severity, need_type = score_with_llm(inc["description"])
        dup_id = find_duplicate(inc, open_incidents)
        if dup_id:
            sb_request(f"incidents?id=eq.{inc['id']}", "PATCH",
                       {"severity": severity, "need_type": need_type, "status": "resolved", "duplicate_of": dup_id})
            log(inc["id"], "flagged_duplicate", f"duplicate of incident {dup_id}")
            print(f"#{inc['id']}: duplicate of #{dup_id}")
        else:
            sb_request(f"incidents?id=eq.{inc['id']}", "PATCH",
                       {"severity": severity, "need_type": need_type, "status": "triaged"})
            log(inc["id"], "triaged", f"severity {severity}, need {need_type}")
            print(f"#{inc['id']}: triaged severity={severity} need={need_type}")


if __name__ == "__main__":
    if "--loop" in sys.argv:
        while True:
            process_once()
            time.sleep(10)
    else:
        process_once()
