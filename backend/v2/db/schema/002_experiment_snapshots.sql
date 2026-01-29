-- ============================================================
-- File: 002_experiment_snapshots.sql
-- Location: backend/v2/db/schema/
--
-- Purpose:
--   Read-optimized snapshot of the latest experiment state.
--   Used for dashboards, filters, and fast queries.
--
-- Notes:
--   - This table is DERIVED from experiment_events
--   - This table is MUTABLE
--   - This table can be rebuilt at any time
-- ============================================================

CREATE TABLE IF NOT EXISTS experiment_snapshots (

    -- One row per experiment
    experiment_id UUID PRIMARY KEY,

    -- Owning user
    user_id UUID NOT NULL,

    -- Human-readable metadata
    name TEXT NOT NULL,
    team TEXT,
    
    -- Derived state
    current_status TEXT NOT NULL,
    current_phase INTEGER NOT NULL CHECK (current_phase BETWEEN 1 AND 7),

    -- Risk indicators
    has_warnings BOOLEAN NOT NULL DEFAULT FALSE,
    has_override BOOLEAN NOT NULL DEFAULT FALSE,

    -- Locked design info (nullable until Phase 4)
    locked_version INTEGER,
    primary_metric TEXT,
    metric_type TEXT,

    mde DOUBLE PRECISION,
    power DOUBLE PRECISION,
    confidence DOUBLE PRECISION,

    -- Outcome (nullable until Phase 6/7)
    winning_variant TEXT,
    decision TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL,
    last_updated_at TIMESTAMPTZ NOT NULL
);

-- ============================================================
-- Indexes for fast dashboard queries
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_snapshots_user
ON experiment_snapshots (user_id);

CREATE INDEX IF NOT EXISTS idx_snapshots_status
ON experiment_snapshots (current_status);

CREATE INDEX IF NOT EXISTS idx_snapshots_phase
ON experiment_snapshots (current_phase);

CREATE INDEX IF NOT EXISTS idx_snapshots_risk
ON experiment_snapshots (has_warnings, has_override);

CREATE INDEX IF NOT EXISTS idx_snapshots_updated
ON experiment_snapshots (last_updated_at);
