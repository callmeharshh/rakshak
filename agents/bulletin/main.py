"""
Bulletin agent -- stub.

Nothing in this file is implemented. See README.md in this folder.
"""


def poll_confirmed_dispatches(db):
    raise NotImplementedError("built during the AgentX hackathon window")


def draft_update(incident) -> str:
    """LLM call: short plain-language status update for the ward."""
    raise NotImplementedError("built during the AgentX hackathon window")


def translate(text: str, language: str) -> str:
    """LLM call: translate `text` into incidents.language ('hi' or 'mr')."""
    raise NotImplementedError("built during the AgentX hackathon window")


def send_whatsapp(to: str, message: str):
    """Twilio WhatsApp sandbox send."""
    raise NotImplementedError("built during the AgentX hackathon window")


def run():
    raise NotImplementedError("built during the AgentX hackathon window")


if __name__ == "__main__":
    run()
