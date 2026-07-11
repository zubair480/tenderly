-- The catalog is provider-neutral. This field existed only for a removed
-- connector and has no role in matching or generic opportunity ingestion.
ALTER TABLE opportunities DROP COLUMN IF EXISTS apply_on_idealist;
