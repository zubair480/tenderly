"""Pure, unit-testable opportunity scoring and ranking.

Formula (kept identical to docs/AI-AND-DATA.md so frontend and backend teams
agree on what a "match" means):

    base_score = 0.45*skills_overlap + 0.25*cause_alignment
               + 0.20*availability_fit + 0.10*neighborhood_relevance
    final_score = clamp(base_score + scenario_needs_boost, 0, 1)
"""

SURGE_BOOST_CATEGORIES = {"food_security", "homelessness"}

FLEXIBLE_TOKENS = {"flexible", "any", "anytime", "any time"}


def normalize_neighborhood_key(name: str) -> str:
    """Normalize a neighborhood string for cross-source lookup.

    Collapses whitespace and lowercases rather than title-casing, since
    Socrata's `neighborhoods_sffind_boundaries` field has raw entries in both
    Title Case and ALL CAPS for the same neighborhood, and titles like
    "South of Market" would otherwise mismatch a naive `.title()` call
    (which capitalizes "of").
    """
    return " ".join((name or "").strip().split()).lower()


def _normalize_set(items: list[str]) -> set[str]:
    return {i.strip().lower() for i in items if i and i.strip()}


def overlap_fraction(profile_items: list[str], target_items: list[str]) -> float:
    """Fraction of `target_items` satisfied by `profile_items`, 0..1.

    Exact (case-insensitive) matches count fully; remaining unmatched target
    items get partial credit if a profile item is a substring match (e.g.
    profile skill "driving" against opportunity requirement
    "valid driver's license").
    """
    target_set = _normalize_set(target_items)
    profile_set = _normalize_set(profile_items)
    if not target_set or not profile_set:
        return 0.0

    exact = target_set & profile_set
    score = len(exact) / len(target_set)

    remaining = target_set - exact
    if remaining:
        partial_hits = 0
        for t in remaining:
            if any(t in p or p in t for p in profile_set):
                partial_hits += 1
        score += (partial_hits / len(remaining)) * 0.5 * (len(remaining) / len(target_set))

    return min(score, 1.0)


def availability_fit(profile_availability: str, opportunity_availability: list[str]) -> float:
    """Score how well a profile's availability string fits an opportunity.

    The real frontend (frontend/src/constants.ts) sends exactly one of
    "one_time", "weekly", or "flexible" - not the day/time-of-day strings
    ("weekends", "weekday evenings") this task's contract example showed.
    Opportunity availability tags are day/time-of-day based. Handled as an
    opaque string either way so both vocabularies score sensibly.
    """
    pa = (profile_availability or "").strip().lower()
    if not pa:
        return 0.5

    opp_tokens = [a.strip().lower() for a in opportunity_availability]

    # A volunteer who says they're flexible fits any opportunity's schedule,
    # regardless of whether the opportunity itself is tagged "flexible".
    if pa in FLEXIBLE_TOKENS:
        return 1.0

    if pa in opp_tokens:
        return 1.0
    if any(t in FLEXIBLE_TOKENS for t in opp_tokens):
        return 0.85

    pa_words = set(pa.replace("-", " ").replace("_", " ").split())
    for t in opp_tokens:
        t_words = set(t.replace("-", " ").replace("_", " ").split())
        if pa_words & t_words:
            return 0.6

    # "one_time"/"weekly" don't map to any day/time-of-day tag, but a
    # one-off shift or an ongoing weekly commitment can both realistically
    # fit most of these opportunities - moderate, not full, credit.
    if pa in ("one_time", "one time"):
        return 0.7
    if pa == "weekly":
        return 0.55

    return 0.25


def neighborhood_relevance(neighborhood: str, neighborhood_case_counts: dict[str, int]) -> float:
    """0..1 density of live community need in this opportunity's neighborhood."""
    if not neighborhood_case_counts:
        return 0.2

    max_count = max(neighborhood_case_counts.values())
    if max_count <= 0:
        return 0.2

    key = normalize_neighborhood_key(neighborhood)
    count = neighborhood_case_counts.get(key, 0)
    return min(count / max_count, 1.0)


def scenario_needs_boost(
    category: str, neighborhood_score: float, encampment_share: float, scenario: str
) -> float:
    """Extra score added only in scenario=surge, only for surge-relevant categories.

    Scaled by both general neighborhood case density and that neighborhood's
    share of cases specifically tagged Encampment-related, so a cold-snap
    surge favors neighborhoods where the live data shows the most
    homelessness-adjacent strain, not just the busiest 311 neighborhoods.
    """
    if scenario == "surge" and category in SURGE_BOOST_CATEGORIES:
        return round(0.15 * (0.5 + neighborhood_score) + 0.25 * encampment_share, 4)
    return 0.0


def urgency_label(
    base_urgency: float,
    neighborhood_score: float,
    encampment_share: float,
    scenario: str,
    category: str,
) -> tuple[str, float]:
    urgency_score = 0.5 * base_urgency + 0.5 * neighborhood_score
    if scenario == "surge" and category in SURGE_BOOST_CATEGORIES:
        urgency_score = min(urgency_score + 0.2 + 0.2 * encampment_share, 1.0)

    if urgency_score < 0.4:
        return "low", urgency_score
    if urgency_score < 0.7:
        return "medium", urgency_score
    return "high", urgency_score


def score_opportunity(
    profile: dict,
    opportunity: dict,
    neighborhood_case_counts: dict[str, int],
    scenario: str,
    neighborhood_encampment_share: dict[str, float] | None = None,
) -> dict:
    encampment_shares = neighborhood_encampment_share or {}
    key = normalize_neighborhood_key(opportunity.get("neighborhood", ""))
    encampment_share = encampment_shares.get(key, 0.0)

    skills_overlap = overlap_fraction(profile.get("skills", []), opportunity.get("needed_skills", []))
    cause_alignment = overlap_fraction(profile.get("causes", []), opportunity.get("causes", []))
    availability = availability_fit(profile.get("availability", ""), opportunity.get("availability", []))
    neighborhood_score = neighborhood_relevance(opportunity.get("neighborhood", ""), neighborhood_case_counts)

    base_score = (
        0.45 * skills_overlap + 0.25 * cause_alignment + 0.20 * availability + 0.10 * neighborhood_score
    )
    boost = scenario_needs_boost(opportunity.get("category", ""), neighborhood_score, encampment_share, scenario)
    final_score = max(0.0, min(base_score + boost, 1.0))

    label, urgency_score = urgency_label(
        opportunity.get("base_urgency", 0.5),
        neighborhood_score,
        encampment_share,
        scenario,
        opportunity.get("category", ""),
    )

    return {
        "score": round(final_score, 4),
        "urgency": label,
        "urgency_score": round(urgency_score, 4),
    }


def rank_opportunities(
    profile: dict,
    opportunities: list[dict],
    neighborhood_case_counts: dict[str, int],
    scenario: str,
    neighborhood_encampment_share: dict[str, float] | None = None,
) -> list[dict]:
    scored = []
    for opp in opportunities:
        result = score_opportunity(
            profile, opp, neighborhood_case_counts, scenario, neighborhood_encampment_share
        )
        scored.append({**opp, **result})

    scored.sort(key=lambda o: (-o["score"], -o["urgency_score"], o["org_name"]))
    return scored
