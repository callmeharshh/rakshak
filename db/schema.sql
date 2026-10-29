-- RAKSHAK database schema
-- Pre-hackathon scaffold. This is the "shared blackboard" described in the idea deck:
-- Sentinel, Dispatch and Bulletin all read and write these same tables instead of
-- passing messages through a framework or a queue.

CREATE TABLE incidents (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    source          TEXT NOT NULL,              -- 'sos_sms' | 'sos_whatsapp' | 'mock_imd_alert' | 'social'
    ward            TEXT NOT NULL,
    lat             DOUBLE PRECISION NOT NULL,
    lon             DOUBLE PRECISION NOT NULL,
    description     TEXT NOT NULL,
    need_type       TEXT NOT NULL,              -- 'rescue' | 'medical' | 'food' | 'shelter' | 'water'
    language        TEXT NOT NULL,              -- 'hi' | 'mr'
    severity        SMALLINT,                   -- 1-5, filled in by Sentinel (built during the hackathon)
    status          TEXT NOT NULL DEFAULT 'new',-- 'new' | 'triaged' | 'dispatched' | 'resolved'
    duplicate_of    INTEGER REFERENCES incidents(id)
);

CREATE TABLE volunteers (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    resource_type   TEXT NOT NULL,              -- 'boat_team' | 'medical_team' | 'relief_truck' | 'shelter_coordinator' | 'rescue_squad'
    lat             DOUBLE PRECISION NOT NULL,
    lon             DOUBLE PRECISION NOT NULL,
    capacity        SMALLINT NOT NULL,
    available       BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE dispatch_log (
    id                      SERIAL PRIMARY KEY,
    incident_id             INTEGER NOT NULL REFERENCES incidents(id),
    volunteer_id            INTEGER NOT NULL REFERENCES volunteers(id),
    assigned_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    resources_committed     SMALLINT NOT NULL DEFAULT 1,
    -- the guardrail from the idea deck, encoded as a real column, not a slide bullet:
    needs_human_approval    BOOLEAN NOT NULL DEFAULT false, -- true when resources_committed > 2 OR incident.severity >= 4
    approved_by_human       BOOLEAN,
    approved_at             TIMESTAMPTZ
);

CREATE TABLE activity_log (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    agent_name  TEXT NOT NULL,          -- 'sentinel' | 'dispatch' | 'bulletin' | 'human'
    incident_id INTEGER REFERENCES incidents(id),
    action      TEXT NOT NULL,
    details     TEXT
);
