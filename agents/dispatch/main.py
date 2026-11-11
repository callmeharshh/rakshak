"""
Dispatch agent.

Polls `incidents` where status = 'triaged', matches each to the nearest available
volunteer of a matching resource_type (Haversine distance), and writes a dispatch_log
row. The guardrail: dispatches needing more than 2 resources, or for severity >= 4
incidents, are held for a human to approve from the dashboard instead of auto-confirming.

Run once:  python3 agents/dispatch/main.py
Poll loop: python3 agents/dispatch/main.py --loop
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import sb_request, haversine_km, log_activity  # noqa: E402

NEED_TO_RESOURCE = {
    "rescue": "rescue_squad",
    "medical": "medical_team",
    "food": "relief_truck",
    "shelter": "shelter_coordinator",
    "water": "relief_truck",
}


def resources_for(severity):
    return min(3, max(1, severity - 2))


def nearest_volunteer(incident, volunteers):
    wanted = NEED_TO_RESOURCE.get(incident["need_type"])
    candidates = [v for v in volunteers if v["available"] and v["resource_type"] == wanted]
    if not candidates:
        return None
    return min(candidates, key=lambda v: haversine_km(incident["lat"], incident["lon"], v["lat"], v["lon"]))


def process_once():
    triaged = sb_request("incidents?status=eq.triaged&select=*")
    if not triaged:
        print("no triaged incidents")
        return
    volunteers = sb_request("volunteers?select=*")

    for inc in triaged:
        volunteer = nearest_volunteer(inc, volunteers)
        if not volunteer:
            print(f"#{inc['id']}: no available volunteer for need_type={inc['need_type']}")
            continue

        resources = resources_for(inc["severity"])
        needs_approval = resources > 2 or inc["severity"] >= 4

        sb_request("dispatch_log", "POST", {
            "incident_id": inc["id"], "volunteer_id": volunteer["id"],
            "resources_committed": resources, "needs_human_approval": needs_approval,
            "approved_by_human": False if needs_approval else True,
        })

        if needs_approval:
            log_activity("dispatch", inc["id"], "held_for_approval",
                          f"{volunteer['name']} ({resources} resources) -- severity {inc['severity']}, awaiting human approval")
            print(f"#{inc['id']}: HELD for approval -> {volunteer['name']} ({resources} resources)")
        else:
            sb_request(f"incidents?id=eq.{inc['id']}", "PATCH", {"status": "dispatched"})
            log_activity("dispatch", inc["id"], "dispatched", f"{volunteer['name']} ({resources} resources), auto-confirmed")
            print(f"#{inc['id']}: dispatched -> {volunteer['name']} ({resources} resources)")


if __name__ == "__main__":
    if "--loop" in sys.argv:
        while True:
            process_once()
            time.sleep(10)
    else:
        process_once()
