# AI and data plan

## What AI does—and does not do

AI performs two useful, bounded tasks:

1. **Profile extraction:** transform a volunteer’s resume into a concise structured profile: likely skills, an experience summary, and relevant cause signals.
2. **Grounded explanation:** turn the match factors into a plain-language `why_you` statement that identifies the relevant skills, commitment, and current need.

AI does **not** decide whether someone is qualified, eligible, safe, or morally better suited to volunteer. It suggests opportunities and explains the rationale; the user remains the decision-maker.

## DigitalOcean AI Platform plan

Use the DigitalOcean AI Platform from the backend for model inference. The backend owns the credentials and sends only the minimal resume text/extracted content needed for the prompt.

| Step | Input | Output | Guardrail |
| --- | --- | --- | --- |
| Resume-to-profile | Text extracted server-side from PDF/TXT, plus user-selected causes/availability | Contract-shaped profile fields | Schema validation; discard unknown fields; do not infer protected attributes. |
| Explanation generation | Selected skills, opportunity facts, score factors, scenario/needs context | One short `why_you` statement | No fabricated nonprofit claims; fall back if output is missing or invalid. |

The demo should state this plainly: “DigitalOcean AI Platform turns experience into a structured, explainable volunteer profile; Tenderly’s backend then combines that profile with local needs.” That connects sponsor technology to an actual product outcome.

## Matching model: transparent and implementable

Use an explainable weighted score rather than claiming opaque precision.

```text
base_score =
  0.45 * skills_overlap +
  0.25 * cause_alignment +
  0.20 * availability_fit +
  0.10 * neighborhood_relevance

final_score = clamp(base_score + scenario_needs_boost, 0, 1)
```

For a cold snap, boost opportunities tagged with weather-response, shelter, food, or outreach categories in neighborhoods with elevated related needs. The response’s `needs_summary` must say this in ordinary language, e.g., “A cold snap is increasing outreach and warming-center demand in the Tenderloin and SoMa, so weather-response roles moved up.”

### Why this is better for the demo

- It is easy to explain in a sentence.
- The re-rank has a visible, defensible causal explanation.
- It lets the UI show useful score percentages without implying a prediction of a person’s behavior.
- It is stable in mock mode and flexible in production.

## Community-needs data

The backend owns retrieval and normalization of San Francisco open-data signals. The browser receives only the compact `GET /api/needs` response it needs to render the pulse.

### Data rules

- Record the source timestamp and show `updated_at` as a human-readable freshness label.
- Maintain a small mapping from source categories to Tenderly opportunity categories.
- Cache source results and label stale data honestly rather than presenting it as live.
- Use counts as directional context, not as a claim that an individual neighborhood or person is in crisis.
- Keep source URLs and query details in backend documentation once the exact dataset is finalized.

## Evaluation before presenting

Test with at least three supplied demo profiles (for example: operations professional, bilingual student mentor, and healthcare volunteer) and verify:

- Each gets three materially different, relevant recommendations.
- The explanation cites only known profile and opportunity facts.
- The surge scenario changes at least two ranks and explains the change.
- A missing AI response falls back gracefully.
- No profile describes a protected trait or makes an eligibility judgment.
