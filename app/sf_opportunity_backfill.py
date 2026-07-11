"""Bounded, evidence-first SF volunteer-opportunity backfill using MiMo.

This is intentionally conservative: a page must be on an official nonprofit
domain, explicitly describe a volunteer role, give a street address, and
geocode inside the SF metro radius before Tenderly can recommend it.
"""

import hashlib
import json
import logging
import math
import os
import re
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from app.config import GRADIENT_API_KEY, GRADIENT_BASE_URL
from app.gradient_client import call_llm_json
from app.opportunity_ingestion import _PageTextExtractor
from app.opportunity_repository import create_import, finish_import, save_import_records

logger = logging.getLogger("tenderly.sf_backfill")

MIMO_MODEL = "mimo-v2.5"
SF_SPENDING_URL = "https://data.sfgov.org/resource/qkex-vh98.json"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
SF_LATITUDE = 37.7749
SF_LONGITUDE = -122.4194
SF_RADIUS_MILES = 30
DISCOVERY_BATCH_SIZE = 1
MAX_PAGE_TEXT_CHARS = 18_000
BLOCKED_DOMAINS = {
    "indeed.com",
    "linkedin.com",
    "idealist.org",
    "volunteermatch.org",
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com",
}
URL_PATTERN = re.compile(r"https?://[^\s\]\[\"'<>)}]+")
PRIORITY_SF_NONPROFITS = [
    "826 Valencia",
    "GLIDE",
    "San Francisco-Marin Food Bank",
    "San Francisco AIDS Foundation",
    "Catholic Charities San Francisco",
    "Project Open Hand",
    "St. Anthony Foundation",
    "San Francisco SPCA",
    "San Francisco Education Fund",
    "Meals on Wheels San Francisco",
    "Shanti Project",
    "Hamilton Families",
    "Larkin Street Youth Services",
    "Self-Help for the Elderly",
    "Boys & Girls Clubs of San Francisco",
    "San Francisco Village",
    "Mission Neighborhood Centers",
    "Bay Area Women and Children's Center",
    "Community Youth Center of San Francisco",
    "SF Bicycle Coalition",
]


EXTRACTION_SYSTEM_PROMPT = """You extract real volunteer opportunities from one official nonprofit page.
Return ONLY a valid JSON object: {"opportunities": [...]}. Every item must have exactly these keys:
org_name, title, description, commitment, availability, needed_skills, causes, street_address, city,
state, postal_code, evidence, confidence.

Rules:
- Include a role only when the supplied page explicitly describes a current volunteer role or shift.
- The evidence value must be a short exact sentence from the supplied page proving that role exists.
- Never infer a street address, schedule, skill, cause, availability, or role title.
- Use null for unknown single values and [] for unknown arrays.
- Exclude generic “learn more” or “sign up to volunteer” pages without a distinct role.
- confidence is 0 through 1. Return an empty opportunities array if nothing qualifies."""


def _distance_miles(latitude: float, longitude: float) -> float:
    lat_delta = math.radians(latitude - SF_LATITUDE)
    lng_delta = math.radians(longitude - SF_LONGITUDE)
    a = (
        math.sin(lat_delta / 2) ** 2
        + math.cos(math.radians(SF_LATITUDE))
        * math.cos(math.radians(latitude))
        * math.sin(lng_delta / 2) ** 2
    )
    return 3958.8 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_good_sf_location(latitude: float, longitude: float) -> bool:
    return _distance_miles(latitude, longitude) <= SF_RADIUS_MILES


def _normalize_tags(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return sorted({item.strip().lower() for item in value if isinstance(item, str) and item.strip()})


def _is_official_candidate_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return False
    return not any(host == domain or host.endswith(f".{domain}") for domain in BLOCKED_DOMAINS)


def sf_nonprofit_names(limit: int = 1_000) -> list[str]:
    """Get unique nonprofit vendors from San Francisco's open spending data."""
    response = httpx.get(
        SF_SPENDING_URL,
        params={
            "$select": "supplier_name",
            "$where": "nonprofit='Nonprofit'",
            "$group": "supplier_name",
            "$order": "supplier_name",
            "$limit": str(limit),
        },
        timeout=30,
    )
    response.raise_for_status()
    names = []
    for row in response.json():
        name = str(row.get("supplier_name") or "").strip()
        if len(name) >= 4 and any(character.isalpha() for character in name):
            names.append(name)
    return names


def _output_text(response: dict[str, Any]) -> str:
    text_parts: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                text_parts.append(text)
    # Incomplete responses can still contain useful, source-page URLs in
    # reasoning blocks, so retain them for the URL-only discovery stage.
    return "\n".join(text_parts) or json.dumps(response)


def discover_official_volunteer_urls(organization_names: list[str]) -> list[str]:
    """Use DigitalOcean MiMo web search to find official volunteer pages only."""
    names = "; ".join(organization_names)
    prompt = (
        "For each San Francisco nonprofit below, use web search to find its official HTTPS volunteer page. "
        "Return only official nonprofit-domain URLs that explicitly advertise volunteering. Do not return job boards, "
        "directories, social media, or a search-results page.\n\nOrganizations: "
        f"{names}"
    )
    response = httpx.post(
        f"{GRADIENT_BASE_URL.rstrip('/')}/responses",
        headers={"Authorization": f"Bearer {GRADIENT_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MIMO_MODEL,
            "input": prompt,
            "tools": [{"type": "web_search", "max_uses": 1, "max_results": 8}],
            "max_output_tokens": 400,
        },
        timeout=90,
    )
    response.raise_for_status()
    urls = {match.rstrip(".,;:") for match in URL_PATTERN.findall(_output_text(response.json()))}
    return sorted(url for url in urls if _is_official_candidate_url(url))


def fetch_page_text(url: str) -> str | None:
    response = httpx.get(
        url,
        headers={"User-Agent": "TenderlyOpportunityResearch/1.0 (contact: hello@tenderly.app)"},
        follow_redirects=True,
        timeout=30,
    )
    response.raise_for_status()
    if "html" not in response.headers.get("content-type", ""):
        return None
    parser = _PageTextExtractor()
    parser.feed(response.text)
    text = parser.text()
    return text[:MAX_PAGE_TEXT_CHARS] if text else None


def geocode_sf_address(address: str) -> tuple[float, float] | None:
    response = httpx.get(
        NOMINATIM_URL,
        params={"q": address, "format": "jsonv2", "limit": "1", "countrycodes": "us"},
        headers={"User-Agent": "TenderlyOpportunityResearch/1.0 (contact: hello@tenderly.app)"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if not data:
        return None
    latitude, longitude = float(data[0]["lat"]), float(data[0]["lon"])
    return (latitude, longitude) if is_good_sf_location(latitude, longitude) else None


def _build_record(raw: dict[str, Any], source_url: str) -> dict[str, Any] | None:
    org_name = str(raw.get("org_name") or "").strip()
    title = str(raw.get("title") or "").strip()
    description = str(raw.get("description") or "").strip()
    evidence = str(raw.get("evidence") or "").strip()
    street_address = str(raw.get("street_address") or "").strip()
    city = str(raw.get("city") or "").strip()
    state = str(raw.get("state") or "").strip()
    postal_code = str(raw.get("postal_code") or "").strip()
    try:
        confidence = float(raw.get("confidence"))
    except (TypeError, ValueError):
        confidence = 0.0

    if not all((org_name, title, description, evidence, street_address, city, state)) or confidence < 0.9:
        return None
    address = ", ".join(part for part in (street_address, city, state, postal_code) if part)
    location = geocode_sf_address(address)
    if location is None:
        return None
    latitude, longitude = location
    identity = f"{source_url}|{title}|{address}".lower()
    source_key = f"sf_verified_web:{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]}"
    causes = _normalize_tags(raw.get("causes"))

    return {
        "source_id": "sf_verified_web",
        "source_key": source_key,
        "org_name": org_name[:200],
        "title": title[:200],
        "description": description[:4_000],
        "category": causes[0] if causes else "community",
        "neighborhood": city[:120],
        "lat": latitude,
        "lng": longitude,
        "commitment": str(raw.get("commitment") or "See official role details")[:240],
        "availability": _normalize_tags(raw.get("availability")),
        "needed_skills": _normalize_tags(raw.get("needed_skills")),
        "causes": causes,
        "base_urgency": 0.5,
        "source_url": source_url,
        "confidence": confidence,
        "source_metadata": {
            "source_payload": {"evidence": evidence, "extracted": raw},
            "address": {
                "full": address,
                "line1": street_address,
                "city": city,
                "state": state,
                "zipcode": postal_code,
                "latitude": latitude,
                "longitude": longitude,
            },
            "location_type": "onsite",
            "provider_functions": _normalize_tags(raw.get("needed_skills")),
            "areas_of_focus": causes,
            "times_of_day": _normalize_tags(raw.get("availability")),
            "other_requirements": evidence,
        },
    }


def extract_page_records(source_url: str, page_text: str) -> list[dict[str, Any]]:
    prompt = (
        f"Official source URL: {source_url}\n\n"
        f"Page text:\n{page_text}"
    )
    raw = call_llm_json(
        EXTRACTION_SYSTEM_PROMPT,
        prompt,
        {"opportunities": []},
        max_tokens=1_200,
        temperature=0.0,
        timeout_seconds=30,
        model=MIMO_MODEL,
        json_mode=True,
    )
    candidates = raw.get("opportunities", []) if isinstance(raw, dict) else []
    return [record for candidate in candidates if (record := _build_record(candidate, source_url)) is not None]


def run_backfill(target: int = 1_000, duration_seconds: int = 600) -> dict[str, int]:
    """Run for no more than the requested budget and promote only validated roles."""
    started_at = time.monotonic()
    public_dataset_names = sf_nonprofit_names(limit=1_000)
    names = list(dict.fromkeys(PRIORITY_SF_NONPROFITS + public_dataset_names))
    seen_urls: set[str] = set()
    totals = {"organizations_checked": 0, "pages_checked": 0, "promoted": 0, "skipped": 0}

    for index in range(0, len(names), DISCOVERY_BATCH_SIZE):
        if totals["promoted"] >= target or time.monotonic() - started_at >= duration_seconds:
            break
        batch = names[index : index + DISCOVERY_BATCH_SIZE]
        totals["organizations_checked"] += len(batch)
        try:
            urls = discover_official_volunteer_urls(batch)
        except Exception as exc:  # Discovery failures should not end the timed run.
            logger.warning("source discovery failed for batch=%s error=%s", batch, exc)
            continue

        for url in urls:
            if totals["promoted"] >= target or time.monotonic() - started_at >= duration_seconds:
                break
            if url in seen_urls:
                continue
            seen_urls.add(url)
            try:
                page_text = fetch_page_text(url)
                if not page_text:
                    totals["skipped"] += 1
                    continue
                content_hash = hashlib.sha256(page_text.encode("utf-8")).hexdigest()
                import_id = create_import("sf_verified_web", url, content_hash, page_text)
                if import_id is None:
                    totals["skipped"] += 1
                    continue
                records = extract_page_records(url, page_text)
                remaining = max(target - totals["promoted"], 0)
                records = records[:remaining]
                promoted = save_import_records(import_id, records, [])
                finish_import(import_id, "parsed", parsed_records=records)
                totals["pages_checked"] += 1
                totals["promoted"] += promoted
                time.sleep(1.1)  # Respect Nominatim's public-service usage guidance.
            except Exception as exc:
                logger.warning("source ingestion failed url=%s error=%s", url, exc)
                totals["skipped"] += 1
        logger.info("backfill progress=%s elapsed_seconds=%d", totals, time.monotonic() - started_at)

    return totals


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    target = int(os.environ.get("SF_BACKFILL_TARGET", "1000"))
    minutes = int(os.environ.get("SF_BACKFILL_MINUTES", "10"))
    logger.info("SF opportunity backfill finished: %s", run_backfill(target=target, duration_seconds=minutes * 60))


if __name__ == "__main__":
    main()
