# Dispatch

**Status: built.** Polls `incidents` where `status = 'triaged'`, matches each to the
nearest available volunteer of a matching `resource_type` (Haversine distance), and
writes a `dispatch_log` row.

The guardrail: `resources_committed = min(3, max(1, severity - 2))`. Anything with
`resources_committed > 2` or `severity >= 4` is held with `needs_human_approval = true`
until someone taps **Approve** on the dashboard; everything smaller auto-confirms
immediately. Either way it's logged to `activity_log`.

Run once: `python3 agents/dispatch/main.py`
Poll loop: `python3 agents/dispatch/main.py --loop`
