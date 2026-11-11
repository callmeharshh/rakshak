"""Shared plumbing for the three agents: env loading, Supabase REST, Haversine distance."""
import json
import math
import os
import urllib.request


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
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


def sb_request(path, method="GET", body=None, return_repr=False):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
        headers["Prefer"] = "return=representation" if return_repr else "return=minimal"
    req = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{path}", method=method, data=data, headers=headers)
    resp = urllib.request.urlopen(req).read()
    return json.loads(resp) if resp else None


def groq_chat(prompt, max_tokens=300):
    body = json.dumps({
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": max_tokens,
        "reasoning_effort": "low",
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions", method="POST", data=body,
        # Groq sits behind Cloudflare, which blocks urllib's default User-Agent -- needs a real one.
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json", "User-Agent": "rakshak/1.0"},
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp["choices"][0]["message"]["content"]


WARDS = {
    "Kurla": (19.0728, 72.8826, "mr"), "Sion": (19.0448, 72.8626, "hi"),
    "Dharavi": (19.0411, 72.8514, "mr"), "Chembur": (19.0522, 72.9005, "mr"),
    "Bandra": (19.0596, 72.8295, "hi"), "Andheri": (19.1136, 72.8697, "mr"),
    "Wadala": (19.0176, 72.8565, "mr"), "Matunga": (19.0273, 72.8554, "mr"),
    "Santacruz": (19.0821, 72.8411, "mr"),
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


assert haversine_km(19.0, 72.8, 19.0, 72.8) < 1e-9  # same point -> 0 km, sanity check


def log_activity(agent_name, incident_id, action, details=""):
    sb_request("activity_log", "POST", {"agent_name": agent_name, "incident_id": incident_id, "action": action, "details": details})
