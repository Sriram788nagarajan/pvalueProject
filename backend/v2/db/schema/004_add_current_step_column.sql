ALTER TABLE experiment_snapshots
ADD COLUMN IF NOT EXISTS current_step TEXT;