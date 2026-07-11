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


def test_name_extracted_when_pdf_splits_each_word_onto_its_own_line():
    # Real bytes captured from production logs: this specific PDF's text
    # layer extracts one word per line, with stray whitespace-only lines
    # in between, instead of collapsing the header into one line or
    # keeping normal multi-word lines.
    header = (
        "Muhammad\n \nZubair\n \nZafar\n \ngithub .com/zubair480\n \n|\n \n"
        "linkedin.com/in/zubair480\n \n|\n \n(\n217)\n \n790\n \n8056\n \n|\n \n"
        "zubairzafar480@gmail.com\n \n|\n \n94103,\n \nSF\n \nEDUCATION"
    )
    profile = build_fallback_profile(header, [])
    assert profile["name"] == "Muhammad Zubair Zafar"


def test_name_extracted_when_pdf_collapses_header_into_one_line():
    # pypdf commonly collapses a resume's name + GitHub/LinkedIn/phone/email
    # header into a single line with no newlines. The whole line clearly
    # isn't just a name, but a name-shaped word run still starts it.
    header = (
        "Muhammad Zubair Zafar github.com/zubair480 | linkedin.com/in/zubair480 "
        "| (217) 790 8056 | zubairzafar480@gmail.com | 94103, SF EDUCATION "
        "Eastern Illinois University, IL"
    )
    profile = build_fallback_profile(header, [])
    assert profile["name"] == "Muhammad Zubair Zafar"


def test_skills_subcategory_label_is_stripped_not_fused_with_value():
    text = "SKILLS\nLanguages: Python, TypeScript, Java"
    profile = build_fallback_profile(text, [])
    assert profile["skills"] == ["python", "typescript", "java"]


def test_multiple_skill_subcategories_on_separate_lines_dont_fuse():
    text = "SKILLS\nLanguages: Python, Java\nTools: Git, Docker"
    profile = build_fallback_profile(text, [])
    assert profile["skills"] == ["python", "java", "git", "docker"]


def test_empty_resume_uses_generic_summary():
    profile = build_fallback_profile("", [])
    assert profile["name"] == "Volunteer"
    assert profile["experience_summary"]
    assert profile["skills"] == ["teamwork", "communication", "reliability"]
