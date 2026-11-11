# Sentinel

**Status: built.** Polls `incidents` where `status = 'new'`, scores severity + need_type
via an LLM (Groq, `openai/gpt-oss-120b`), checks for a same-ward duplicate within 500m
using the Haversine formula, and writes the result plus an `activity_log` row.

Note on scope: dedupe currently matches on ward + 500m radius, not a time window — fine
for the demo dataset, a real deployment would also bound it by recency.

Run once: `python3 agents/sentinel/main.py`
Poll loop: `python3 agents/sentinel/main.py --loop`
