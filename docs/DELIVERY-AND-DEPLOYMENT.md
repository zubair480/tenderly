# Delivery and DigitalOcean deployment

## Deployment choice

Deploy Tenderly on **DigitalOcean App Platform**:

- **Frontend:** a Static Site built from this Vite repository, publishing `dist/`.
- **Backend:** a Web Service (the parallel team’s API) that exposes the agreed `/api` endpoints.
- **AI:** backend integration with the DigitalOcean AI Platform; keys remain server-side.

This makes DigitalOcean an active part of the product, not merely a hosting badge. It also creates a simple story for the sponsor prize: App Platform delivers the user experience, and the AI Platform powers structured profile creation and grounded explanations.

## Frontend build settings

| App Platform setting | Value |
| --- | --- |
| Source | Git repository and production branch |
| Component type | Static Site |
| Build command | `npm ci && npm run build` |
| Output directory | `dist` |
| Node version | Pin in `.nvmrc` or `engines` after the scaffold chooses a current LTS release |

The frontend must be a standard Vite static build: no server rendering, API proxy, or runtime secret is required.

## Environment configuration

| Variable | Local mock | Preview/production |
| --- | --- | --- |
| `VITE_USE_MOCK` | `true` | `false` once backend is stable; `true` is acceptable only for an intentional demo fallback. |
| `VITE_API_URL` | `http://localhost:8080` | Deployed API public URL, e.g. `https://api-<app>.ondigitalocean.app` |

Vite values are compiled at build time. Update an App Platform environment variable and trigger/redeploy a new build; changing it after the build will not alter a static bundle.

## Backend requirements for deployment

- Bind to the port supplied by the platform.
- Set allowed CORS origins to the frontend App Platform domain and local Vite origin for development.
- Validate uploads server-side and delete temporary resume files promptly.
- Keep DigitalOcean AI credentials in backend encrypted environment variables, never in frontend config or Git.
- Cache the normalized SF data snapshot with a recorded update time so transient source failure does not break the user flow.

## Release checklist

1. Run `npm ci` and `npm run build` locally from a clean checkout.
2. Test the deployed frontend URL in an incognito window.
3. Confirm browser requests target the expected API URL, not localhost.
4. Complete the normal flow and cold-snap scenario on the deployed site.
5. Confirm a bad network/API response produces a retry state.
6. Complete the keyboard audit and 375px/1440px responsive checks on the deployed build.
7. Check that DevTools/source maps/network logs contain no secrets or resume content.
8. Save the deployed URLs in the Devpost submission before the deadline.

## Rollback and demo contingency

- **Frontend failure:** redeploy the last known-good static build from the same commit/branch.
- **Backend/AI failure:** deploy or select mock mode only if necessary for the demo; be honest that the mock is deterministic demo data and point judges to the contract-compatible real client.
- **External data failure:** serve a clearly timestamped cached pulse; never show invented “live” conditions.
- **Last 30 minutes:** freeze feature work. Only verify the live link, rehearse, and submit.

## Proof for the DigitalOcean track

Capture two screenshots before submission:

1. The App Platform overview showing the deployed frontend/backend components (without secrets).
2. The working Tenderly profile-to-matches flow, where the `why you` explanation is visible.

In the Devpost description, name both services and say what each one does. Avoid vague wording such as “powered by AI.”
