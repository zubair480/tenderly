# Opportunity ingestion on DigitalOcean

Tenderly's opportunity catalog is designed to update automatically without allowing an AI model to quietly publish unverified roles.

## What runs every six hours

The `opportunity-ingestion` DigitalOcean App Platform job runs at minute zero, every six hours, in the `America/Los_Angeles` time zone. The schedule is defined in [`.do/app.yaml`](../.do/app.yaml).

```text
Approved source → fetch → content hash → DigitalOcean AI parser
                → validation → staging/audit tables → active opportunities
```

- An unchanged source hash skips the model call.
- Invalid records never enter matching.
- Records below the source confidence threshold remain in `opportunity_staging` for a human to review.
- A valid, high-confidence role is upserted into `opportunities` and is available to the matching API immediately.
- A role disappears from two successful, non-empty source runs before Tenderly pauses it. A temporary source failure cannot remove roles.

The scheduled job starts with no external source enabled. This is intentional: an organization should approve automated access before Tenderly fetches its pages. The job is live and ready; enabling a vetted source is a one-line configuration change followed by a deployment.

## Source configuration

[`data/opportunity_sources.json`](../data/opportunity_sources.json) is the single, readable source registry. Each entry explains its organization, URL allowlist, default location/category values, confidence threshold, and activation condition.

Current candidate sources:

| Source | Type | Status | Why it is useful |
| --- | --- | --- | --- |
| 826 Valencia | Static volunteer page | Awaiting approval | Education and youth tutoring roles |
| GLIDE | Static volunteer page | Awaiting approval | Food security and homelessness roles |
| SF-Marin Food Bank | Static volunteer page | Awaiting approval | Food-security roles |
| Partner JSON feed template | JSON API | Ready to configure | Preferred path for scalable partner integrations |

SF 311 is not an opportunity source. It remains a separate live community-needs input for ranking and surge simulation.

### Enable an approved source

1. Get approval from the nonprofit or use its documented API/feed.
2. Confirm the source URL and every hostname in `allowed_domains`.
3. Set that source's `enabled` field to `true`.
4. Commit and deploy. The next scheduled run discovers it automatically.
5. Check App Platform job logs and the staging table after the first run.

For a JSON or Airtable-based partner feed, copy `partner_json_feed_template`, give it a unique `id`, set its real HTTPS URL and allowlist, then enable it. JSON feeds are preferable to HTML because their data is less ambiguous and less likely to change page structure.

## AI parser configuration

[`data/opportunity_parser.json`](../data/opportunity_parser.json) keeps the model choice, temperature, allowed categories, required fields, and promotion policy in plain language.

The ingestion job calls DigitalOcean Serverless Inference through the existing `GRADIENT_MODEL` setting. Its job is strictly extraction and normalization into JSON. It does not score volunteers, choose recommendations, or make live matching decisions.

The parser receives only public source content and source defaults. It must provide a per-record confidence score and cannot introduce a link outside the source's configured allowlist.

## Database tables

| Table | Purpose |
| --- | --- |
| `organizations` | One row per nonprofit organization |
| `opportunities` | Active catalog read by the matching API |
| `opportunity_imports` | Raw source snapshot, content hash, parser result, and errors |
| `opportunity_staging` | Valid but pending, auto-approved, or rejected records |

The idempotent schema is in [`db/migrations/001_opportunity_catalog.sql`](../db/migrations/001_opportunity_catalog.sql). The `db-migrate` pre-deploy job applies it and seeds the curated local catalog once, so a new production database does not start empty.

## Local verification

Use these commands after configuring a development PostgreSQL `DATABASE_URL`:

```bash
python -m app.migrate
OPPORTUNITY_INGESTION_ENABLED=true python -m app.ingestion_job
```

Without `DATABASE_URL`, the public API safely continues to read [`data/opportunities.json`](../data/opportunities.json), which keeps frontend development and the hackathon demo working.

## DigitalOcean setup

The App Platform spec creates/binds a Managed PostgreSQL component named `tenderly-db` and passes its generated `DATABASE_URL` to the API, migration job, and ingestion job. Do not hardcode a database password.

The scheduled job configuration follows DigitalOcean's documented `SCHEDULED` job format and costs only while it runs. See [DigitalOcean’s scheduled-job guide](https://docs.digitalocean.com/products/app-platform/how-to/manage-jobs/) and [database environment-variable guide](https://docs.digitalocean.com/products/app-platform/how-to/use-environment-variables/).
