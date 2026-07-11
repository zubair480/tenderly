from app.matching import (
    availability_fit,
    normalize_neighborhood_key,
    overlap_fraction,
    rank_opportunities,
    score_opportunity,
)


def test_overlap_fraction_exact_match():
    assert overlap_fraction(["python", "teaching"], ["python"]) == 1.0


def test_overlap_fraction_partial_credit():
    score = overlap_fraction(["driving"], ["driving a delivery van"])
    assert 0.0 < score < 1.0


def test_overlap_fraction_empty_inputs():
    assert overlap_fraction([], ["python"]) == 0.0
    assert overlap_fraction(["python"], []) == 0.0


def test_availability_fit_exact_match():
    assert availability_fit("weekends", ["weekends", "flexible"]) == 1.0


def test_availability_fit_flexible_opportunity():
    assert availability_fit("weekday mornings", ["flexible"]) == 0.85


def test_availability_fit_no_match():
    assert availability_fit("weekday mornings", ["weekend evenings"]) == 0.25


def test_normalize_neighborhood_key_handles_case_and_whitespace():
    assert normalize_neighborhood_key("SOUTH OF MARKET") == normalize_neighborhood_key("South of Market  ")


def _sample_profile():
    return {
        "skills": ["cooking", "teamwork", "physical labor"],
        "causes": ["food security", "homelessness"],
        "availability": "weekday evenings",
    }


def _sample_opportunity(category="food_security", neighborhood="Tenderloin"):
    return {
        "opportunity_id": "test-opp",
        "org_name": "Test Org",
        "title": "Test Role",
        "category": category,
        "neighborhood": neighborhood,
        "needed_skills": ["cooking", "teamwork", "food safety"],
        "causes": ["food security", "homelessness"],
        "commitment": "3 hrs",
        "base_urgency": 0.6,
    }


def test_score_opportunity_within_bounds():
    profile = _sample_profile()
    opp = _sample_opportunity()
    result = score_opportunity(profile, opp, {"tenderloin": 10}, "normal")
    assert 0.0 <= result["score"] <= 1.0
    assert result["urgency"] in ("low", "medium", "high")


def test_surge_scenario_boosts_relevant_category():
    profile = _sample_profile()
    opp = _sample_opportunity(category="food_security", neighborhood="Tenderloin")
    case_counts = {"tenderloin": 100, "mission": 10}
    encampment_share = {"tenderloin": 0.5}

    normal = score_opportunity(profile, opp, case_counts, "normal", encampment_share)
    surge = score_opportunity(profile, opp, case_counts, "surge", encampment_share)

    assert surge["score"] > normal["score"]


def test_surge_scenario_does_not_boost_unrelated_category():
    profile = _sample_profile()
    opp = _sample_opportunity(category="animal_welfare", neighborhood="Tenderloin")
    case_counts = {"tenderloin": 100}
    encampment_share = {"tenderloin": 0.5}

    normal = score_opportunity(profile, opp, case_counts, "normal", encampment_share)
    surge = score_opportunity(profile, opp, case_counts, "surge", encampment_share)

    assert surge["score"] == normal["score"]


def test_rank_opportunities_sorts_descending_by_score():
    profile = _sample_profile()
    strong_match = _sample_opportunity(category="food_security", neighborhood="Tenderloin")
    strong_match["opportunity_id"] = "strong"
    weak_match = {
        **_sample_opportunity(category="animal_welfare", neighborhood="Portola"),
        "opportunity_id": "weak",
        "needed_skills": ["animal handling"],
        "causes": ["animal welfare"],
    }

    ranked = rank_opportunities(profile, [weak_match, strong_match], {"tenderloin": 10}, "normal")

    assert [r["opportunity_id"] for r in ranked] == ["strong", "weak"]
    assert ranked[0]["score"] >= ranked[1]["score"]
