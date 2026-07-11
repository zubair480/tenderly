# API contract and frontend integration

The following response shapes are fixed. Frontend code may add TypeScript types and client helpers but must not rename fields or change request/response shape.

## Runtime configuration

```bash
# .env.example
VITE_API_URL=http://localhost:8080
VITE_USE_MOCK=true
```

- `VITE_API_URL` defaults to `http://localhost:8080` when absent.
- Treat `VITE_USE_MOCK` as `true` unless its exact value is `false`. This keeps a fresh demo safe before backend integration.
- Do not place any secret in a `VITE_*` variable.

## Contract types

```ts
export type Availability = string;
export type Scenario = 'normal' | 'surge';
export type Urgency = 'low' | 'medium' | 'high';

export interface Profile {
  profile_id: string;
  name: string;
  skills: string[];
  experience_summary: string;
  causes: string[];
  availability: Availability;
}

export interface Match {
  opportunity_id: string;
  org_name: string;
  title: string;
  category: string;
  neighborhood: string;
  lat: number;
  lng: number;
  commitment: string;
  score: number;
  urgency: Urgency;
  why_you: string | null;
}

export interface MatchesResponse {
  matches: Match[];
  scenario: Scenario;
  needs_summary: string;
}

export interface NeighborhoodNeed {
  name: string;
  case_count: number;
  top_categories: string[];
}

export interface NeedsResponse {
  updated_at: string;
  neighborhoods: NeighborhoodNeed[];
}
```

## Endpoints

### `POST /api/profile`

Submit `multipart/form-data` with the exact keys below.

| Form key | Type | Notes |
| --- | --- | --- |
| `file` | `File` | PDF or TXT, optional only for a documented sample-profile demo path if backend supports it. |
| `interests` | string | Serialize selected causes consistently with backend agreement; default recommendation is JSON string array. Confirm this integration detail before production cutover. |
| `availability` | string | Selected availability value. |

Response: `Profile`

### `GET /api/matches/{profile_id}?scenario=normal|surge`

Response: `MatchesResponse`

- The UI must retain `opportunity_id` as the Framer Motion `layoutId`/React key so re-ordering is legible.
- `score` is a float from 0–1. Display `Math.round(score * 100)` with “match” text.
- `why_you` may be `null`; this is not an error.

### `GET /api/needs`

Response: `NeedsResponse`

- Parse `updated_at` defensively. If formatting fails, show “Recently updated” rather than an invalid date.
- Show only the most relevant 3–5 neighborhoods so the pulse remains readable.

## Client behavior

```ts
export interface TenderlyApi {
  createProfile(input: {
    file: File;
    interests: string[];
    availability: string;
  }): Promise<Profile>;
  getMatches(profileId: string, scenario: Scenario): Promise<MatchesResponse>;
  getNeeds(): Promise<NeedsResponse>;
}
```

`mock.ts` and `client.ts` must both implement this interface. `api/index.ts` chooses one implementation based on `VITE_USE_MOCK`. The UI imports only from `api/index.ts`.

## Error contract for the UI

The client helper must throw a typed or normalized error with a user-safe message. Components display only generic recovery copy; they must not render raw server error bodies, source URLs, or stack traces.

## Integration checklist

- [ ] Test form-data keys and `interests` serialization with backend before changing mock default.
- [ ] Confirm CORS for deployed frontend origin.
- [ ] Confirm whether profile IDs expire and how long mock/real sessions remain valid.
- [ ] Verify a normal request, surge request, and `why_you: null` response against the UI.
- [ ] Verify an HTTP 4xx, 5xx, and offline case each show a retryable state.
