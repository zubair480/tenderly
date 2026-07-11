from app.opportunity_ingestion import _PageTextExtractor, enabled_sources, normalize_candidate


def _parser_config() -> dict:
    return {
        "allowed_categories": ["education", "community"],
        "promotion_policy": {"minimum_confidence": 0.9},
    }


def _source() -> dict:
    return {
        "id": "example",
        "url": "https://volunteer.example.org/roles",
        "allowed_domains": ["volunteer.example.org"],
        "defaults": {
            "category": "education",
            "neighborhood": "Mission",
            "lat": 37.76,
            "lng": -122.42,
            "causes": ["education"],
            "base_urgency": 0.5,
        },
    }


def test_enabled_sources_requires_explicit_true() -> None:
    sources = enabled_sources({"sources": [{"id": "on", "enabled": True}, {"id": "off", "enabled": False}]})
    assert [source["id"] for source in sources] == ["on"]


def test_normalize_candidate_applies_safe_defaults_and_allowlist() -> None:
    record, error = normalize_candidate(
        {
            "external_id": "tutor-1",
            "org_name": "Example Org",
            "title": "Writing Tutor",
            "description": "Support students with writing practice.",
            "category": "education",
            "commitment": "2 hours each week",
            "availability": ["weekday afternoons"],
            "needed_skills": ["writing", "teaching"],
            "causes": ["education"],
            "source_url": "https://untrusted.example.net/role/1",
            "confidence": 0.96,
        },
        _source(),
        _parser_config(),
    )

    assert error is None
    assert record is not None
    assert record["source_url"] == "https://volunteer.example.org/roles"
    assert record["neighborhood"] == "Mission"
    assert record["confidence"] == 0.96
    assert record["source_key"].startswith("example:")


def test_html_text_extractor_ignores_scripts() -> None:
    parser = _PageTextExtractor()
    parser.feed("<h1>Volunteer today</h1><script>secret()</script><p>Help students.</p>")
    assert parser.text() == "Volunteer today\nHelp students."
