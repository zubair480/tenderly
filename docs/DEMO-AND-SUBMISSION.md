# Demo and submission plan

## Four-minute live demo script

### 0:00–0:30 — Human problem

“A lot of people want to volunteer, but an open directory makes them do all the work: they have to interpret what every organization needs and guess whether their own skills matter. Tenderly turns that uncertainty into one clear next step for San Francisco.”

Show the landing statement and the uncluttered onboarding form.

### 0:30–1:10 — Volunteer input

Upload a prepared PDF/TXT resume or choose the sample profile. Select causes and availability. Briefly point out that the form works with keyboard and does not ask someone to create an account before helping.

### 1:10–1:40 — AI profile

Show the loading state, then the profile reveal. Say: “Our backend uses DigitalOcean AI Platform to translate experience into a small, structured volunteer profile. We keep the output explainable and never use it to make an eligibility decision.”

### 1:40–2:35 — Three meaningful matches

Show the first card’s `why you` block before discussing its percentage. Explain that Tenderly uses skills, stated causes, availability, and neighborhood context, then tells the volunteer why the result is useful. Point out the commitment and urgency label so a user can decide without digging.

### 2:35–3:20 — The data/AI moment

Open Community pulse, then trigger “Simulate: cold snap hits SF.” Pause for the re-rank. Say: “This is the difference between a directory and a decision tool: when neighborhood demand shifts, Tenderly changes the recommendation and says why.”

### 3:20–4:00 — Completion and impact

Say: “Tenderly is deployed on DigitalOcean App Platform. It couples AI-assisted personal context with local data and an accessible interface so a willing volunteer can find a meaningful place to help today.”

End on the top match and its explanation, not on source code.

## Demo discipline

- Seed the exact sample profile before judges arrive.
- Keep a second browser tab or deployment URL in mock mode as fallback.
- Never rely on a freshly uploaded personal resume or untested live data.
- Use the same scenario every rehearsal so rank changes are predictable.
- Do not narrate every technical implementation detail. Show the user outcome first, then name the technology supporting it.

## Devpost submission checklist

The [official event page](https://ai-for-social-good-mlh.devpost.com/) requires a Devpost submission and in-person judging. Complete these before the deadline.

- [ ] Project name: **Tenderly**
- [ ] One-line tagline from `DESCRIPTION.md`
- [ ] Project description: problem, solution, local impact, AI/data method, and DigitalOcean usage
- [ ] “How we built it”: React, Vite, TypeScript, Tailwind, Framer Motion, API service, DigitalOcean App Platform, DigitalOcean AI Platform, and SF open data
- [ ] Live deployed URL
- [ ] Source repository URL
- [ ] Short demo video or live-demo-ready walkthrough, if submission form asks for it
- [ ] Two DigitalOcean proof screenshots
- [ ] Any team member and eligibility fields completed
- [ ] Submitted on Devpost before 5:00pm PDT; confirm receipt in the UI

## Submission copy starter

**What it does:** Tenderly helps San Franciscans turn the desire to volunteer into a meaningful next step. It extracts a concise skills profile from a resume, recommends three local nonprofit opportunities, and explains why each one fits.

**Why it matters:** Volunteer opportunities are easy to find but difficult to evaluate. Tenderly combines someone’s skills and availability with a community-needs pulse so they can see where they can help now—not just browse a static list.

**DigitalOcean use:** Tenderly is deployed with DigitalOcean App Platform. Its backend uses DigitalOcean AI Platform to create a structured volunteer profile and grounded match explanations, while SF open-data signals re-rank recommendations when community conditions change.
