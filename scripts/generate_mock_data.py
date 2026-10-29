#!/usr/bin/env python3
"""
Generates the seeded mock dataset used for:
  - db/seed_data.sql          (so the schema can be populated once a real DB exists)
  - dashboard/data/mock.json  (consumed by the static dashboard preview)

This is fabricated example data for a simulated Mumbai flood scenario, used only to
design and preview the dashboard UI before the hackathon. No agent has produced any
of this - it is hand-templated, not triaged or dispatched by anything.

Run: python3 scripts/generate_mock_data.py
"""
import json
import random
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).resolve().parent.parent

WARDS = {
    "Kurla": (19.0728, 72.8826, "mr"),
    "Sion": (19.0448, 72.8626, "hi"),
    "Dharavi": (19.0411, 72.8514, "mr"),
    "Chembur": (19.0522, 72.9005, "mr"),
    "Bandra": (19.0596, 72.8295, "hi"),
    "Andheri": (19.1136, 72.8697, "mr"),
    "Kalyan": (19.2403, 73.1305, "mr"),
    "Vikhroli": (19.1072, 72.9262, "mr"),
    "Govandi": (19.0550, 72.9150, "hi"),
    "Mankhurd": (19.0470, 72.9330, "hi"),
    "Wadala": (19.0176, 72.8565, "mr"),
    "Parel": (18.9947, 72.8325, "mr"),
    "Byculla": (18.9750, 72.8325, "hi"),
    "Matunga": (19.0273, 72.8554, "mr"),
    "Santacruz": (19.0821, 72.8411, "mr"),
}

NEED_TEMPLATES = {
    "rescue": "Waterlogging near {ward} station road; family of {n} stranded on the first floor, water still rising.",
    "medical": "Elderly resident near {ward} needs urgent medical evacuation; pre-existing heart condition, can't wade out.",
    "food": "Shelter near {ward} community hall now holding about {n} people, running low on food and drinking water.",
    "shelter": "Partial roof collapse risk reported near {ward} chawl; residents asking for temporary shelter.",
    "water": "No safe drinking water near {ward} for over a day; several households affected.",
}
NEED_TYPES = list(NEED_TEMPLATES.keys())
SOURCES = ["sos_whatsapp", "sos_sms", "mock_imd_alert", "social"]
STATUSES = ["new", "new", "triaged", "triaged", "dispatched", "dispatched", "resolved"]

VOLUNTEER_NAMES = [
    "Asha Patil", "Ramesh Kadam", "Fatima Shaikh", "Vikram Nair", "Sunita More",
    "Imran Shaikh", "Priya Desai", "Sandeep Gupta", "Lata Joshi", "Faizan Ansari",
    "Anjali Rao", "Manoj Pawar", "Kavita Iyer", "Suresh Yadav", "Neha Kulkarni",
]
RESOURCE_TYPES = ["boat_team", "medical_team", "relief_truck", "shelter_coordinator", "rescue_squad"]


def jitter(lat, lon, spread=0.01):
    return round(lat + random.uniform(-spread, spread), 6), round(lon + random.uniform(-spread, spread), 6)


def build_incidents(count=45):
    incidents = []
    ward_names = list(WARDS.keys())
    for i in range(1, count + 1):
        ward = random.choice(ward_names)
        lat0, lon0, lang = WARDS[ward]
        lat, lon = jitter(lat0, lon0)
        need_type = random.choice(NEED_TYPES)
        n = random.choice([2, 3, 4, 5, 6, 8, 12])
        description = NEED_TEMPLATES[need_type].format(ward=ward, n=n)
        incidents.append({
            "id": i,
            "source": random.choice(SOURCES),
            "ward": ward,
            "lat": lat,
            "lon": lon,
            "description": description,
            "need_type": need_type,
            "language": lang,
            "severity": random.randint(1, 5),
            "status": random.choice(STATUSES),
            "duplicate_of": None,
        })
    # mark a few as duplicates of an earlier nearby incident, since that's the one
    # behaviour Sentinel is explicitly meant to catch
    for dup_idx in random.sample(range(10, count), 4):
        incidents[dup_idx]["duplicate_of"] = random.randint(1, dup_idx - 1)
        incidents[dup_idx]["status"] = "resolved"
    return incidents


def build_volunteers(count=15):
    volunteers = []
    ward_names = list(WARDS.keys())
    for i in range(1, count + 1):
        ward = random.choice(ward_names)
        lat0, lon0, _ = WARDS[ward]
        lat, lon = jitter(lat0, lon0, spread=0.015)
        volunteers.append({
            "id": i,
            "name": VOLUNTEER_NAMES[(i - 1) % len(VOLUNTEER_NAMES)],
            "resource_type": RESOURCE_TYPES[i % len(RESOURCE_TYPES)],
            "lat": lat,
            "lon": lon,
            "capacity": random.randint(2, 10),
            "available": random.random() > 0.3,
        })
    return volunteers


def to_sql(incidents, volunteers) -> str:
    lines = ["-- Fabricated example data for UI design purposes only.",
             "-- See scripts/generate_mock_data.py for how this was generated.", ""]
    for v in volunteers:
        lines.append(
            "INSERT INTO volunteers (id, name, resource_type, lat, lon, capacity, available) "
            f"VALUES ({v['id']}, '{v['name']}', '{v['resource_type']}', {v['lat']}, {v['lon']}, "
            f"{v['capacity']}, {str(v['available']).lower()});"
        )
    lines.append("")
    for inc in incidents:
        desc = inc["description"].replace("'", "''")
        dup = "NULL" if inc["duplicate_of"] is None else str(inc["duplicate_of"])
        lines.append(
            "INSERT INTO incidents (id, source, ward, lat, lon, description, need_type, language, "
            f"severity, status, duplicate_of) VALUES ({inc['id']}, '{inc['source']}', '{inc['ward']}', "
            f"{inc['lat']}, {inc['lon']}, '{desc}', '{inc['need_type']}', '{inc['language']}', "
            f"{inc['severity']}, '{inc['status']}', {dup});"
        )
    return "\n".join(lines) + "\n"


def main():
    incidents = build_incidents()
    volunteers = build_volunteers()

    sql_path = ROOT / "db" / "seed_data.sql"
    sql_path.write_text(to_sql(incidents, volunteers))
    print(f"wrote {sql_path}")

    json_path = ROOT / "dashboard" / "data" / "mock.json"
    json_path.write_text(json.dumps({"incidents": incidents, "volunteers": volunteers}, indent=2))
    print(f"wrote {json_path}")


if __name__ == "__main__":
    main()
