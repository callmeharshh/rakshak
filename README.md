# RAKSHAK

PS-03 &middot; Multi-Agent Disaster Response Coordinator
Team **Smooth Operator** &middot; AgentX Hackathon 2026

## Status: pre-hackathon scaffold

This repo is **not** the hackathon project yet. It's repo structure, a database schema,
seeded mock data, and a static UI preview of the dashboard &mdash; the "hour 0-4" work from
our build plan (below), done ahead of time so we can start building the actual agents the
moment the clock starts.

**Sentinel, Dispatch and Bulletin are not implemented.** They'll be built live during the
official 24-hour window: **11 Nov 2026, 10:00 AM &rarr; 12 Nov 2026, 10:00 AM IST**, per the
AgentX Hackathon 2026 rules. The stub files under `agents/` say so explicitly, and every
one of their functions raises `NotImplementedError`.

Live preview of the dashboard mockup: **https://rakshak-ps03-smoothoperator.netlify.app**

## The problem

Every monsoon, control rooms try to track SOS calls, volunteer availability and relief
stock across phone calls, WhatsApp groups and spreadsheets no single person can see all
of at once. The resources are usually already in the district &mdash; a boat here, a truck
there &mdash; the problem is matching them to the right request before the window to help
closes.

## What we're building

Three agents sharing one incident table, plus a dashboard a human actually controls:

- **Sentinel** &mdash; reads incoming reports, tags location/severity/need, and checks nearby
  open incidents so the same street doesn't get logged five times.
- **Dispatch** &mdash; matches each triaged incident to the nearest available volunteer or
  resource (straight-line distance, not a claim of production routing). Larger assignments
  pause for a human to approve.
- **Bulletin** &mdash; once a dispatch is confirmed, drafts a short update and sends it, for
  real, over Twilio's WhatsApp sandbox, in Hindi or Marathi depending on the ward.
- **The dashboard** &mdash; an incident map (Leaflet + OpenStreetMap, no API key), a live list
  of who's been dispatched where, and a log of every action an agent took.

## How it actually works

- **Shared state:** every agent reads/writes one Postgres table (`db/schema.sql`). No
  message bus, no vector store pretending to be memory.
- **The guardrail:** any dispatch assigning more than two resources, or an incident scored
  severity 4 or 5, is held until a human taps approve on the dashboard. Everything smaller
  auto-confirms, logged either way. See `dispatch_log.needs_human_approval` in the schema.
- **What each agent calls:** an LLM API for severity scoring and translation, the Haversine
  formula for distance (no paid maps API), Twilio's WhatsApp sandbox for real sends,
  Leaflet + OpenStreetMap for the map, Postgres/SQLite for the shared table.

## What we're deliberately not building

- **Live IMD/NDMA integration** &mdash; needs government API access we don't have. We seed a
  realistic mock feed and say so on stage.
- **A custom-trained severity model** &mdash; a scoped prompt does the job for a 24-hour build.
- **Production-grade translation** &mdash; the LLM translates directly. Fine for a demo, not a
  claim that it's ready to ship.
- **A real volunteer network** &mdash; a seeded, fictional roster, clearly marked as mock data.

## Repo layout

```
db/schema.sql               the shared tables: incidents, volunteers, dispatch_log, activity_log
db/seed_data.sql            generated mock data (Mumbai flood scenario), for once a real DB exists
scripts/generate_mock_data.py   single source of truth for the mock data above and dashboard/data/mock.json
agents/sentinel/             stub -- built hours 4-10 of the hackathon
agents/dispatch/             stub -- built hours 10-16
agents/bulletin/              stub -- built hours 16-20
dashboard/                   static UI preview (what's deployed as the live link above)
```

## Hour-by-hour plan for Nov 11&ndash;12

| Hours | Work |
|---|---|
| 0&ndash;4h | Repo, DB schema, seed data, skeleton dashboard &mdash; **this is what's in this repo today.** |
| 4&ndash;10h | Sentinel: ingestion, severity scoring, the dedupe check. |
| 10&ndash;16h | Dispatch: matching logic, the approval guardrail, wired into the dashboard. |
| 16&ndash;20h | Bulletin: message drafting, translation, the actual Twilio WhatsApp send. |
| 20&ndash;24h | Fix what's broken, rehearse the demo twice, leave a buffer. |

## Team

Smooth Operator
