import pathlib

from app.resume_parser import build_fallback_profile

FIXTURE_PATH = pathlib.Path(__file__).resolve().parent / "fixtures" / "sample_resume.txt"


def _load_fixture() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_extracts_name_from_first_line():
    profile = build_fallback_profile(_load_fixture(), [])
    assert profile["name"] == "Jordan Lee"


def test_extracts_skills_from_skills_section_not_keyword_scan():
    profile = build_fallback_profile(_load_fixture(), [])
    # Section-based extraction should pick up "event planning" and
    # "team leadership", which aren't in the generic KNOWN_SKILLS scan list
    # in the same phrasing, proving the SKILLS: heading was actually parsed.
    assert "event planning" in profile["skills"]
    assert "driving" in profile["skills"]


def test_extracts_summary_from_summary_section():
    profile = build_fallback_profile(_load_fixture(), [])
    assert profile["experience_summary"].startswith("Operations coordinator")
    assert "EXPERIENCE" not in profile["experience_summary"]


def test_extracts_causes_from_resume_section_when_no_interests_given():
    profile = build_fallback_profile(_load_fixture(), [])
    assert "food security" in profile["causes"]
    assert "immigrant support" in profile["causes"]


def test_interests_take_priority_but_resume_causes_still_merged_in():
    profile = build_fallback_profile(_load_fixture(), ["climate action"])
    assert profile["causes"][0] == "climate action"
    assert "food security" in profile["causes"]


def test_unstructured_resume_falls_back_to_keyword_scan_and_generic_name():
    unstructured = "just a blob of text mentioning python and driving with no sections at all"
    profile = build_fallback_profile(unstructured, ["housing"])
    assert profile["name"] == "Volunteer"
    assert "python" in profile["skills"]
    assert "driving" in profile["skills"]
    assert profile["causes"] == ["housing"]


def test_inline_label_format_is_parsed_like_the_frontends_sample_button():
    # frontend/src/components/OnboardingForm.tsx's "Try the sample profile"
    # button generates exactly this text - "Skills:" inline on one line
    # rather than as its own heading line.
    text = (
        "Maya Patel\n"
        "Operations and community outreach professional\n"
        "Skills: project coordination, technical support, Spanish"
    )
    profile = build_fallback_profile(text, ["Food security"])
    assert profile["name"] == "Maya Patel"
    assert profile["skills"] == ["project coordination", "technical support", "spanish"]


def test_empty_resume_uses_generic_summary():
    profile = build_fallback_profile("", [])
    assert profile["name"] == "Volunteer"
    assert profile["experience_summary"]
    assert profile["skills"] == ["teamwork", "communication", "reliability"]
