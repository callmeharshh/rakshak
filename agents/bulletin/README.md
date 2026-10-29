# Bulletin

**Status: not built yet.** Planned for hours 16-20 of the Nov 11-12 hackathon window.

## Job

1. Poll `dispatch_log` entries that were just confirmed (auto or human-approved).
2. Draft a short, plain-language status update for the affected ward.
3. Translate it into Hindi or Marathi (whichever `incidents.language` says) via an LLM call --
   no separate translation model, no Bhashini/IndicTrans2 infra. Good enough for a demo,
   not a claim that it is production-ready.
4. Send it for real over Twilio's WhatsApp sandbox to a demo number.
5. Write a row to `activity_log`.

## Why it isn't implemented here

Same reason as the other two agents. `main.py` in this folder is a stub only -- and we
don't have Twilio sandbox credentials wired up yet either, on purpose.
