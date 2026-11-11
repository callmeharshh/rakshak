# RAKSHAK

PS-03 &middot; Multi-Agent Disaster Response Coordinator
Team **Smooth Operator** &middot; AgentX Hackathon 2026

## Status: built

All three agents -- Sentinel, Dispatch and Bulletin -- are implemented and tested against
live seeded data, built during the official 24-hour window: **11 Nov 2026, 10:00 AM &rarr;
12 Nov 2026, 10:00 AM IST**, per the AgentX Hackathon 2026 rules.

Live dashboard: **https://rakshak-ps03-smoothoperator.netlify.app**

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
  real, over Telegram, in Hindi or Marathi depending on the ward. (Built on Twilio's
  WhatsApp sandbox first; switched to Telegram when the trial account turned out to have
  no live WhatsApp sending capability -- same job, same real-send guarantee.)
- **The dashboard** &mdash; an incident map (Leaflet + OpenStreetMap, no API key), a live list
  of who's been dispatched where, and a log of every action an agent took.

## How it actually works

- **Shared state:** every agent reads/writes one Postgres table (`db/schema.sql`). No
  message bus, no vector store pretending to be memory.
- **The guardrail:** any dispatch assigning more than two resources, or an incident scored
  severity 4 or 5, is held until a human taps approve on the dashboard. Everything smaller
  auto-confirms, logged either way. See `dispatch_log.needs_human_approval` in the schema.
- **What each agent calls:** Groq (LLM) for severity scoring and translation, the Haversine
  formula for distance (no paid maps API), the Telegram Bot API for real sends, Leaflet +
  OpenStreetMap for the map, Supabase/Postgres for the shared table.

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
agents/sentinel/             built -- severity scoring + dedupe
agents/dispatch/             built -- matching + the approval guardrail
agents/bulletin/              built -- message drafting, translation, the real Telegram send
dashboard/                   live UI, polling Supabase (what's deployed as the live link above)
```

## Team

Smooth Operator
