-- ============================================================
-- File: 001_experiment_events.sql
-- Location: backend/v2/db/schema/
--
-- Purpose:
--   Canonical append-only event store for pvalue.net v2
--   This table is the SINGLE SOURCE OF TRUTH for experiment history.
--
-- Rules:
--   - Append-only (no UPDATE, no DELETE)
--   - One row = one irreversible fact
--   - All experiment state is derived from this table
-- ============================================================

CREATE TABLE IF NOT EXISTS experiment_events (

    -- Unique, time-sortable identifier for the event
    event_id UUID PRIMARY KEY,

    -- Logical experiment identifier (all events for one experiment share this)
    experiment_id UUID NOT NULL,

    -- User who triggered the event (or system user)
    user_id UUID NOT NULL,

    -- What happened (controlled vocabulary, enforced at app level)
    event_type TEXT NOT NULL,

    -- Which phase (1–7) this event belongs to
    phase INTEGER NOT NULL CHECK (phase BETWEEN 1 AND 7),

    -- Importance / risk level of the event
    severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),

    -- When the event occurred (UTC, high precision)
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Version of the event schema (for future evolution)
    schema_version INTEGER NOT NULL DEFAULT 1,

    -- Event-specific structured data
    payload JSONB NOT NULL,

    -- Guardrail: prevent accidental duplicate events
    CONSTRAINT uq_experiment_event UNIQUE (experiment_id, event_id)
);

-- ============================================================
-- Indexes (CRITICAL FOR SCALE)
-- ============================================================

-- Fast timeline reconstruction for a single experiment
CREATE INDEX IF NOT EXISTS idx_events_experiment_time
ON experiment_events (experiment_id, occurred_at);

-- Fast dashboard filtering by user
CREATE INDEX IF NOT EXISTS idx_events_user
ON experiment_events (user_id);

-- Fast filtering by event type (warnings, overrides, decisions)
CREATE INDEX IF NOT EXISTS idx_events_type
ON experiment_events (event_type);

-- Fast filtering by severity (risk analysis)
CREATE INDEX IF NOT EXISTS idx_events_severity
ON experiment_events (severity);

-- Optional: JSONB GIN index for payload searches (future-proof)
CREATE INDEX IF NOT EXISTS idx_events_payload_gin
ON experiment_events
USING GIN (payload);
