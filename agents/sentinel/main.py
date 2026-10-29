"""
Sentinel agent -- stub.

Nothing in this file is implemented. It exists only to show the shape of the agent
before the hackathon starts. See README.md in this folder for what it will do, and
the root README for why we're scaffolding instead of pre-building.
"""


def poll_new_incidents(db):
    """Fetch rows from `incidents` where status = 'new'."""
    raise NotImplementedError("built during the AgentX hackathon window")


def score_severity(incident_text: str) -> int:
    """LLM call: return a 1-5 severity score for a raw incident report."""
    raise NotImplementedError("built during the AgentX hackathon window")


def find_nearby_duplicate(incident, open_incidents, radius_km: float = 0.5, window_hours: int = 6):
    """
    Haversine-distance check against other open incidents in the same ward,
    reported within `window_hours` of each other.
    """
    raise NotImplementedError("built during the AgentX hackathon window")


def run():
    raise NotImplementedError("built during the AgentX hackathon window")


if __name__ == "__main__":
    run()
