# Tenderly frontend

The Tenderly frontend is a single-page React + Vite + TypeScript app. It is intentionally independent from the backend so the full volunteer-matching flow remains demoable while API work continues.

## Run it

```bash
cd frontend
npm install
npm run dev
```

Create a production bundle with `npm run build`. Vite writes the static site to `dist/`.

## API mode

The frontend selects its API implementation at build time:

```bash
VITE_USE_MOCK=true                 # default: local mock responses with a 1.5s delay
VITE_API_URL=http://localhost:8080 # default base URL for the real client
```

Set `VITE_USE_MOCK=false` and set `VITE_API_URL` to the deployed API URL to use the real backend. Never place backend or AI credentials in a `VITE_*` variable: Vite exposes them to the browser.

## API assumptions

These are frontend integration decisions, not changes to the shared contract.

- `POST /api/profile` receives `multipart/form-data` with `file`, `interests`, and `availability` keys. `interests` is serialized as a JSON string array (for example, `["Food security","Digital literacy"]`). The paired backend accepts this format.
- The frontend sends the availability values `one_time`, `weekly`, or `flexible`. The backend treats availability as a string, so it may expose more detailed language later without breaking this client.
- `GET /api/matches/{profile_id}?scenario=normal|surge` returns the fixed `MatchesResponse` shape. The array is already ranked by the backend; the frontend never re-sorts it.
- `GET /api/needs` is independent from match retrieval. If it fails, recommendations remain available and the Community pulse offers its own retry control.
- A missing `why_you` is valid. The UI shows a clear fallback explanation instead of treating it as an API failure.
- The deployed API allows the frontend’s DigitalOcean domain through CORS. The browser sends no authorization header because authentication is out of scope.
- Profile IDs are valid for the duration of this session. The frontend keeps them only in memory and does not persist resumes or profile data.

## Project structure

```text
frontend/
  src/
    api/          # Contract types plus mock and real implementations
    assets/       # Local copies of shared Tenderly visual assets
    components/   # Readable, focused UI sections
    lib/          # Presentation-only helpers
    App.tsx       # Page flow and async state coordination
  .do/app.yaml   # DigitalOcean App Platform static-site spec
```

## Accessibility and interaction checks

- Resume selection works by drag-and-drop and keyboard-accessible file browsing.
- Cause chips and availability controls are keyboard-operable and labeled.
- Loading, profile completion, failures, and scenario updates are announced through polite live regions.
- Urgency and score use text in addition to color/graphics.
- Motion respects `prefers-reduced-motion`.
- Test at 375px and 1440px before submission.

## Assets

The original Stitch exports live in the repository-level `assets/` directory. `src/assets/` contains the same named assets needed for Vite to bundle the logo and visual reference; it uses the same warm terracotta, neutral surface, and editorial typography system.
