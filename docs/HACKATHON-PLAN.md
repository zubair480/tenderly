# Hackathon-winning plan

## Goal

Win by making Tenderly the project that feels both most humane and most complete: a real local problem, substantive AI/data use, an exceptionally clear interface, and a demo that cannot fail.

## What the official brief rewards

The [event page](https://ai-for-social-good-mlh.devpost.com/) lists prize tracks for Best Use of DigitalOcean AI Platform in a Social Good Hack, Best Use of Data, and Best UI/UX. Its general judging asks about originality, technology, design, learning, adherence to the social-good theme, and completion. The plan below deliberately creates evidence for each.

| Judge lens | Tenderly evidence |
| --- | --- |
| Originality | Explainable volunteer matching that shifts with a concrete local-needs signal—not a static directory or opaque score. |
| Technology | Resume extraction, structured profile, transparent multi-factor ranking, scenario re-ranking, mock/real API seam, and DigitalOcean deployment. |
| Design | One-screen onboarding, warm visual identity, readable recommendations, keyboard support, error states, and animated-but-reduced-motion-safe re-ranking. |
| Learning | We use DigitalOcean’s AI Platform and public civic data, then document the tradeoffs and safeguards. |
| Social good | Matches individual capacity to neighborhood-level community needs in San Francisco. |
| Completion | A deployed, seeded demo with mocks that works even if the backend is delayed; the real backend is enabled by configuration. |

## Prize strategy

### Primary target: Best UI/UX

The interface must make the decision simple and dignified. The volunteer sees only the information necessary to act: why this match, how much time it takes, where it is, and how urgent it is. Accessibility is verifiable, not decorative.

### Supporting target: Best Use of Data

The community pulse is not a chart bolted on after matching. It changes the ranking and is explained in plain language. Every data-driven adjustment must be visible to the volunteer.

### Supporting target: Best Use of DigitalOcean AI Platform

Deploy the application on DigitalOcean and have the backend call DigitalOcean’s AI Platform for resume/profile extraction and/or grounded `why_you` generation. In the demo, say exactly which step the platform powers and show the output, not only an API logo.

## Scope: protect the core

### Must ship

- Complete one-page flow from resume upload to recommendations.
- Mock API layer with a deliberate 1.5-second delay and deterministic sample data.
- Real API client behind `VITE_USE_MOCK`.
- AI profile reveal and top-three recommendation cards.
- Community pulse and cold-snap re-ranking scenario.
- DigitalOcean static frontend deployment; backend deployment or a documented handoff path.
- Keyboard, mobile, error, and loading checks.
- Devpost-ready description, architecture, and demo script.

### Only if core is complete

- Interactive Leaflet map with pins for top matches.
- Persisting an optional profile in browser storage.
- Additional scenario simulations.

### Explicitly out of scope for the hackathon

- Authentication, account management, volunteer applications, messaging, payment, and production-grade nonprofit onboarding.
- Making automated eligibility, suitability, or staffing decisions.
- Treating public-data counts as an authoritative measure of an individual’s safety or worthiness.

## Work plan to the deadline

Use this sequence even if one person performs multiple roles. Never hold UI completion for backend readiness.

| Phase | Deliverable | Exit condition |
| --- | --- | --- |
| 1. Foundation | Vite/React/TypeScript/Tailwind scaffold, fonts, tokens, layout shell | `npm run build` succeeds and app renders on mobile. |
| 2. Demo first | Mock module, sample profile, matches, needs data, onboarding and profile flow | A new visitor can reach recommendations without backend. |
| 3. Differentiator | Ranked cards, `why_you`, pulse, cold-snap re-ordering | Ranks visibly change and the explanation banner says why. |
| 4. Integration | Contract-accurate real client and runtime mock switch | Changing one environment variable selects client implementation. |
| 5. Quality | Keyboard pass, loading/error states, 375px/1440px check, reduced-motion check | No blank, unreachable, or unlabeled state remains. |
| 6. Delivery | DigitalOcean deploy, short demo recording/rehearsal, Devpost content | A fresh browser can complete the scripted flow. |

## Time-boxed recovery rules

- If backend integration is not ready, keep mock mode on in the deployed demo and state that the exact production client is already wired behind an environment flag.
- If the map is unfinished, remove it. The pulse and card re-ranking are the meaningful visualization.
- If live SF data is flaky, use a timestamped cached snapshot while retaining the same `GET /api/needs` contract.
- If animation causes instability, prefer a clear before/after banner and stable ranked cards over motion.

## Definition of done

Tenderly is done when a judge can load the deployed link, use a sample resume through keyboard or pointer, understand why the first recommendation is useful, trigger a change in community conditions, and see a credible, accessible answer in under four minutes.
