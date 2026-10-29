# Sentinel

**Status: not built yet.** This is the first agent we build during the hackathon
(planned hours 4-10 of the Nov 11-12 window — see the root README).

## Job

1. Poll `incidents` where `status = 'new'`.
2. Call an LLM to confirm/extract `severity` (1-5) and `need_type` from the raw report text.
3. Check nearby open incidents in the same ward, within a recent time window, using the
   Haversine distance between `(lat, lon)` pairs. If one is close enough in space and time,
   set `duplicate_of` instead of creating a second actionable incident.
4. Set `status = 'triaged'` and write a row to `activity_log`.

## Why it isn't implemented here

We'd rather show up on Nov 11 and build this against the real LLM provider and real
sandbox credentials than ship something today and claim it was built during the
hackathon window. `main.py` in this folder is a stub only.
