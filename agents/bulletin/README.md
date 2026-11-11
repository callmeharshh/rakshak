# Bulletin

**Status: built.** Polls `incidents` where `status = 'dispatched'` and not yet messaged,
drafts a short status update, and sends it for real.

## Job

1. Poll `incidents` where `status = 'dispatched'`, skipping ones already in `activity_log`
   for this agent.
2. Ask an LLM to draft a short, reassuring status update directly in Hindi or Marathi
   (whichever `incidents.language` says) in one call -- no separate translation model.
   Good enough for a demo, not a claim that it is production-ready.
3. Send it for real to the resident's phone. Originally built on Twilio's WhatsApp
   sandbox, but the trial account had no live WhatsApp sending capability (pre-approved
   Content Template sends failed even with Twilio's own example, and SMS required a
   paid number). Switched to the Telegram Bot API instead -- same job (push a real
   message to a real phone, no polling needed on the recipient's end), zero cost, no
   account verification required.
4. Write a row to `activity_log`.

Run once: `python3 agents/bulletin/main.py`
Limit (testing): `python3 agents/bulletin/main.py --limit 1`
Poll loop: `python3 agents/bulletin/main.py --loop`
