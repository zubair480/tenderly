# Backend plan

## Goal

Ship a FastAPI service that satisfies `API-CONTRACT.md` exactly, does real work through DigitalOcean Gradient AI, and re-ranks against live SF 311 data — while never 500ing during the demo.

## How this aligns with the frontend docs

The frontend team already fixed the contract and the scoring philosophy. This plan does not renegotiate them; it implements them.

| Frontend doc | Commitment this backend keeps |
| --- | --- |
| `API-CONTRACT.md` | Response shapes below are byte-exact — no renamed or added top-level fields. |
| `AI-AND-DATA.md` | Uses the published weighted formula (`0.45 skills + 0.25 causes + 0.20 availability + 0.10 neighborhood` + scenario boost, clamped 0–1) instead of inventing new weights. |
| `ARCHITECTURE.md` | AI and data-source credentials stay server-side; CORS restricted in production, open for the hackathon per this task's instructions. |
| `ASSUMPTIONS.md` | Its `interests` serialization question ("JSON string vs comma string") is still open on their side — this backend accepts either, see Assumptions below. |

## Confirmed data facts (checked live against the Socrata API today)

- Dataset `vw6y-z8j6` is actively updated (`max(requested_datetime)` returned `2026-07-10T23:59:34`), so a rolling 7-day window returns real recent rows.
- Relevant fields: `neighborhoods_sffind_boundaries` (neighborhood name), `service_name` (category, e.g. `"Encampments"`), `requested_datetime`.
- Neighborhood names are duplicated in two cases (`"Bayview"` and `"BAYVIEW"`) — every neighborhood must be normalized (title-case, stripped) before grouping or lookup.
- Seed `opportunities.json` neighborhoods will use the exact `neighborhoods_sffind_boundaries` spellings (`"South of Market"` not `"SoMa"`, `"Inner Richmond"` not `"Richmond"`) so urgency lookups join directly without a translation table.

## Scope: protect the golden path

### Must ship
- `POST /api/profile`, `GET /api/matches/{id}`, `GET /api/needs`, `GET /api/health` matching the contract exactly.
- One real Gradient AI call for profile extraction, one batched Gradient AI call for the top-3 `why_you` + `needs_summary`.
- Live Socrata fetch with 10-minute in-memory cache and a bundled snapshot fallback.
- 18 seeded opportunities spanning all 8 required categories, varied enough that different resumes visibly reorder.
- Pure, unit-testable scoring function; `scripts/smoke.sh` exercising the full golden path.
- Dockerfile + `.do/app.yaml` for one-click App Platform deploy on port 8080.

### Only if core is complete
- Fuzzy/embedding-based skill matching (v1 uses keyword/substring overlap).
- Persisting profiles beyond process memory.

### Explicitly out of scope
- Auth, database, request rate limiting, resume retention.

## Work plan

| Phase | Deliverable | Exit condition |
| --- | --- | --- |
| 1. Scaffold | `requirements.txt`, `.env.example`, package layout | `uvicorn app.main:app` boots and `/api/health` returns 200. |
| 2. Seed + scoring | `data/opportunities.json`, `app/matching.py`, `tests/test_matching.py` | Pure scoring function has passing unit tests independent of FastAPI. |
| 3. Gradient client | `app/gradient_client.py` with fence-stripping, retry-once, fallback | Simulated bad JSON output still returns a usable fallback dict. |
| 4. Endpoints | `app/main.py` wiring profile/matches/needs/health | All four endpoints respond with contract-shaped JSON using a sample resume. |
| 5. Needs pipeline | `app/needs_service.py`, `data/needs_snapshot.json` | Socrata outage (simulated by bad URL) falls back to snapshot without breaking `/api/matches`. |
| 6. Smoke + deploy | `scripts/smoke.sh`, `Dockerfile`, `.do/app.yaml` | Smoke script runs green against a locally started server. |

## Time-boxed recovery rules

- If Gradient AI is unreachable during the demo, every LLM call already degrades to a deterministic fallback — the API keeps responding, just without generated prose.
- If Socrata is rate-limited or down, `/api/needs` and the urgency boost fall back to the bundled snapshot, timestamped honestly.
- If the surge scenario doesn't visibly reorder matches for a given resume, that's a seed-data variety problem, not an endpoint problem — fix by widening `base_urgency` spread in `opportunities.json`, not by hardcoding scenario logic.

## Definition of done

A judge (or the frontend teammate) can point `VITE_API_URL` at this service, run the real end-to-end flow with `VITE_USE_MOCK=false`, and get identical shapes to the mock layer — with real Gradient AI text and a real SF 311-driven re-rank on `scenario=surge`.
