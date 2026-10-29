"""
Dispatch agent -- stub.

Nothing in this file is implemented. See README.md in this folder.
"""


def poll_triaged_incidents(db):
    raise NotImplementedError("built during the AgentX hackathon window")


def nearest_available_volunteer(incident, volunteers):
    """Haversine distance to every available, matching-type volunteer; return the closest."""
    raise NotImplementedError("built during the AgentX hackathon window")


def needs_human_approval(resources_committed: int, severity: int) -> bool:
    """True when resources_committed > 2 or severity >= 4 -- the guardrail from the deck."""
    raise NotImplementedError("built during the AgentX hackathon window")


def run():
    raise NotImplementedError("built during the AgentX hackathon window")


if __name__ == "__main__":
    run()
