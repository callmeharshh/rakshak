"""
Sentinel agent.

Polls `incidents` where status = 'new', asks an LLM for severity (1-5) and need_type,
checks for a nearby open duplicate (same ward, within 500m) via the Haversine formula,
and writes the result back to Supabase plus an activity_log row.

Run once:  python3 agents/sentinel/main.py
Poll loop: python3 agents/sentinel/main.py --loop
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import sb_request, groq_chat, haversine_km, log_activity, heartbeat  # noqa: E402


def score_with_llm(description):
    prompt = (
        "You triage disaster-response SOS reports for a flood/heatwave response system in India. "
        "Given the report, reply with ONLY compact JSON, nothing else: "
        '{"severity": <1-5 int, 5 = life-threatening>, "need_type": "<rescue|medical|food|shelter|water>"}\n\n'
        f"Report: {description}"
    )
    text = groq_chat(prompt)
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
            log_activity("sentinel", inc["id"], "flagged_duplicate", f"duplicate of incident {dup_id}")
            print(f"#{inc['id']}: duplicate of #{dup_id}")
        else:
            sb_request(f"incidents?id=eq.{inc['id']}", "PATCH",
                       {"severity": severity, "need_type": need_type, "status": "triaged"})
            log_activity("sentinel", inc["id"], "triaged", f"severity {severity}, need {need_type}")
            print(f"#{inc['id']}: triaged severity={severity} need={need_type}")


if __name__ == "__main__":
    if "--loop" in sys.argv:
        while True:
            try:
                heartbeat("sentinel")
                process_once()
            except Exception as e:
                print(f"loop error (continuing): {e}")
            time.sleep(10)
    else:
        process_once()
