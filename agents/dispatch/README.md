# Dispatch

**Status: not built yet.** Planned for hours 10-16 of the Nov 11-12 hackathon window.

## Job

1. Poll `incidents` where `status = 'triaged'`.
2. Find the nearest `available` volunteer/resource of a matching `resource_type`, using
   straight-line (Haversine) distance against the seeded roster in `volunteers`.
3. Write a `dispatch_log` row. Set `needs_human_approval = true` when
   `resources_committed > 2` or the incident's `severity >= 4` — otherwise auto-confirm.
4. If it needed approval, wait for a human to flip `approved_by_human` from the dashboard
   before marking the incident `dispatched`.
5. Write a row to `activity_log` either way.

## Why it isn't implemented here

Same reason as Sentinel: this is the actual hackathon work, not pre-hackathon scaffolding.
`main.py` in this folder is a stub only.
