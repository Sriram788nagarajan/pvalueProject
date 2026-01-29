ALTER TABLE experiment_snapshots
ADD COLUMN IF NOT EXISTS current_view TEXT;

ALTER TABLE experiment_snapshots
ADD COLUMN IF NOT EXISTS phase1_draft JSONB;

ALTER TABLE experiment_snapshots
ADD COLUMN IF NOT EXISTS phase2_draft JSONB;

ALTER TABLE experiment_snapshots
ADD COLUMN IF NOT EXISTS draft_inputs JSONB;
