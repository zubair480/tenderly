# Backend assumptions

Reasonable calls made while building the backend under a same-day deadline. Full context and
rationale live in `docs/BACKEND-PLAN.md` and `docs/BACKEND-ARCHITECTURE.md`; this file is the
quick-reference version requested alongside the build.

- **`interests` form field** accepts either a JSON array string or a comma-separated string
  (`app/resume_parser.py::parse_interests`), since the frontend's own `docs/ASSUMPTIONS.md` flags
  this serialization as unresolved on their side.
- **`availability` is treated as an opaque string**, matched by keyword/substring rather than a
  fixed enum, since the frontend's `REQUIREMENTS.md` (`one_time`/`weekly`/`flexible`) and this
  task's contract example (`"weekends"`/`"weekday evenings"`) don't agree on vocabulary.
- **Causes vocabulary** in `data/opportunities.json` is the union of the frontend's `REQUIREMENTS.md`
  chip list and the `impact-profile-screen.png` mockup's chip list (they disagree with each other),
  so matching quality holds regardless of which chip set ships.
- **Seed org names** `Code Tenderloin` and `GLIDE` are used verbatim (not generic placeholders)
  because they recur across the teammate's assistant/dashboard/map mockups.
- **Neighborhood spellings** in seed data match Socrata's `neighborhoods_sffind_boundaries` field
  exactly (e.g. `"South of Market"`, `"Inner Richmond"`) so the live-data urgency join needs no
  translation table. Verified live against the dataset before writing seed data.
- **Community urgency signal** combines general 311 case density per neighborhood (all categories)
  with that neighborhood's specific share of `Encampments`-tagged cases (used only for the
  `scenario=surge` boost on `food_security`/`homelessness` categories) - see
  `app/matching.py::scenario_needs_boost`.
- **New product-vision surfaces from `assets/*.png`** (a conversational "Assistant" endpoint, an
  "Expected Impact" match metric) are treated as out of scope for today's frozen API contract, not
  built. Flagged as open items in `docs/BACKEND-PLAN.md`.
- **Gradient AI model/endpoint** default to `llama3.3-70b-instruct` at
  `https://inference.do-ai.run/v1`, both overridable via `GRADIENT_MODEL`/`GRADIENT_BASE_URL` env
  vars since the exact serverless inference endpoint should be verified against current
  DigitalOcean docs before the real demo run.
- **No auth, no database.** Profiles live in an in-memory dict (`app/store.py`) for the process
  lifetime only, per the task's explicit scope.
- **CORS is wide open (`allow_origins=["*"]`)** for the hackathon; the teammate's
  `ARCHITECTURE.md` notes this should be restricted to the deployed frontend domain post-hackathon.
