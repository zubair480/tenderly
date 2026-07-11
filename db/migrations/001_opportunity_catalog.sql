-- Tenderly's production opportunity catalog.
-- The API reads only active rows. Imports are stored separately so every
-- recommendation can be traced back to an approved source and parser run.

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    website TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS opportunity_imports (
    id UUID PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_url TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    parsed_records JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL CHECK (status IN ('started', 'unchanged', 'parsed', 'failed')),
    error_message TEXT,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_id, content_hash)
);

CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id TEXT PRIMARY KEY,
    source_key TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    neighborhood TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    commitment TEXT NOT NULL,
    availability TEXT[] NOT NULL DEFAULT '{}',
    needed_skills TEXT[] NOT NULL DEFAULT '{}',
    causes TEXT[] NOT NULL DEFAULT '{}',
    base_urgency DOUBLE PRECISION NOT NULL DEFAULT 0.5 CHECK (base_urgency >= 0 AND base_urgency <= 1),
    source_url TEXT NOT NULL,
    source_last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'paused', 'closed')),
    missed_source_runs INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS opportunities_active_idx ON opportunities (status, category, neighborhood);
CREATE INDEX IF NOT EXISTS opportunities_source_idx ON opportunities (source_id, source_last_seen_at DESC);

CREATE TABLE IF NOT EXISTS opportunity_staging (
    id UUID PRIMARY KEY,
    import_id UUID NOT NULL REFERENCES opportunity_imports(id) ON DELETE CASCADE,
    source_record_key TEXT NOT NULL,
    candidate JSONB NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    review_status TEXT NOT NULL CHECK (review_status IN ('pending', 'auto_approved', 'rejected')),
    rejection_reason TEXT,
    promoted_opportunity_id TEXT REFERENCES opportunities(opportunity_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at TIMESTAMPTZ,
    UNIQUE (import_id, source_record_key)
);

CREATE INDEX IF NOT EXISTS opportunity_staging_review_idx ON opportunity_staging (review_status, created_at DESC);
