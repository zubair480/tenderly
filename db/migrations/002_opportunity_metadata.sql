-- Preserve source metadata from any volunteer-opportunity feed.
-- Existing core matching columns remain deliberately small and stable; these
-- generic columns make it possible to filter, display, audit, and enrich listings.

ALTER TABLE organizations ADD COLUMN IF NOT EXISTS source_id TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS external_id TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS logo_url TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS areas_of_focus TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS organization_type TEXT;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS address JSONB NOT NULL DEFAULT '{}'::jsonb;
CREATE INDEX IF NOT EXISTS organizations_source_external_idx
    ON organizations (source_id, external_id)
    WHERE source_id IS NOT NULL AND external_id IS NOT NULL;

ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS external_id TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS source_updated_at TIMESTAMPTZ;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS source_first_published_at TIMESTAMPTZ;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS raw_description TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS source_payload JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS address JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS location_type TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS remote_zone TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS remote_country TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS directions TEXT;

ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS application_email TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS application_url TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS application_text TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS application_mode TEXT;

ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS provider_functions TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS areas_of_focus TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS times_of_day TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS expected_time TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS start_date DATE;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS end_date DATE;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS start_time TIME;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS end_time TIME;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS time_zone TEXT;

ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS welcome_groups BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS welcome_families BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS welcome_teens BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS welcome_international BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS welcome_age_55_plus BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS welcome_corporate_groups BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS minimum_age INTEGER;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS orientation_required BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS background_check_required BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS drivers_license_required BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS wheelchair_accessible BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS training_provided BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS stipend_provided BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS fee_required BOOLEAN;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS fee_amount NUMERIC(10,2);
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS other_requirements TEXT;

ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS language TEXT;
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS is_posted_anonymously BOOLEAN;

CREATE UNIQUE INDEX IF NOT EXISTS opportunities_source_external_idx
    ON opportunities (source_id, external_id)
    WHERE external_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS opportunities_source_updated_idx ON opportunities (source_id, source_updated_at DESC);
CREATE INDEX IF NOT EXISTS opportunities_location_idx ON opportunities (location_type, neighborhood);

CREATE TABLE IF NOT EXISTS source_sync_state (
    source_id TEXT PRIMARY KEY,
    cursor_value TEXT,
    last_started_at TIMESTAMPTZ,
    last_completed_at TIMESTAMPTZ,
    last_status TEXT,
    last_error TEXT,
    records_seen INTEGER NOT NULL DEFAULT 0,
    records_upserted INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
