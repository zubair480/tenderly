import json
import logging

from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import needs_service, store
from app.gradient_client import call_llm_json
from app.matching import rank_opportunities
from app.models import HealthResponse, MatchesResponse, NeedsResponse, ProfileResponse
from app.opportunity_repository import load_active_opportunities
from app.resume_parser import (
    PROFILE_SYSTEM_PROMPT,
    build_fallback_profile,
    build_profile_user_prompt,
    extract_resume_text,
    parse_interests,
    sanitize_profile_fields,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tenderly.main")

app = FastAPI(title="Tenderly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

WHY_YOU_SYSTEM_PROMPT = (
    "You are an assistant that writes short volunteer-matching explanations and a community "
    "needs summary for San Francisco. Respond with ONLY a single valid JSON object and nothing "
    "else - no markdown fences, no commentary. The JSON must have exactly these keys: "
    '"needs_summary" (one plain-language sentence describing what San Francisco needs most '
    "right now, grounded only in the neighborhood/category context given below), "
    '"why_you" (an object whose keys are exactly the given opportunity_ids and whose values are '
    "2-3 sentence, second-person explanations that reference the volunteer's specific skills and "
    "the organization's current need - do not invent facts not provided)."
)


def _build_why_you_user_prompt(profile: dict, top_matches: list[dict], needs_payload: dict, scenario: str) -> str:
    profile_summary = {
        "name": profile.get("name"),
        "skills": profile.get("skills"),
        "causes": profile.get("causes"),
        "availability": profile.get("availability"),
    }
    opportunities_summary = [
        {
            "opportunity_id": m["opportunity_id"],
            "org_name": m["org_name"],
            "title": m["title"],
            "category": m["category"],
            "neighborhood": m["neighborhood"],
            "needed_skills": m["needed_skills"],
            "causes": m["causes"],
            "commitment": m["commitment"],
            "urgency": m["urgency"],
        }
        for m in top_matches
    ]
    needs_context = needs_payload.get("neighborhoods", [])[:5]

    return (
        f"Volunteer profile: {json.dumps(profile_summary)}\n\n"
        f"Top matched opportunities: {json.dumps(opportunities_summary)}\n\n"
        f"Current SF community-needs context (top neighborhoods by recent 311 case volume): "
        f"{json.dumps(needs_context)}\n\n"
        f"Scenario: {scenario} "
        f"({'a simulated cold snap is spiking shelter/food demand' if scenario == 'surge' else 'normal conditions'}).\n\n"
        "Produce the JSON now."
    )


def _fallback_why_you_payload(profile: dict, top_matches: list[dict], needs_payload: dict, scenario: str) -> dict:
    skills = profile.get("skills") or ["your background"]
    why_you = {}
    for m in top_matches:
        skill_phrase = skills[0] if skills else "your experience"
        why_you[m["opportunity_id"]] = (
            f"Your experience with {skill_phrase} is a strong fit for {m['org_name']}'s "
            f"{m['title']} role in {m['neighborhood']}, which has a {m['urgency']} current need."
        )

    neighborhoods = needs_payload.get("neighborhoods", [])
    if neighborhoods:
        top = neighborhoods[0]
        category = top["top_categories"][0] if top.get("top_categories") else "community requests"
        if scenario == "surge":
            needs_summary = (
                f"A simulated cold snap is raising shelter and food demand, with {top['name']} "
                f"showing the heaviest recent {category.lower()} activity."
            )
        else:
            needs_summary = f"{top['name']} currently has the most reported {category.lower()} activity in San Francisco."
    else:
        needs_summary = "San Francisco's community needs data is temporarily unavailable, but volunteers are needed citywide."

    return {"needs_summary": needs_summary, "why_you": why_you}


def _sanitize_why_you_payload(data: dict, top_matches: list[dict], fallback: dict) -> dict:
    needs_summary = data.get("needs_summary")
    if not isinstance(needs_summary, str) or not needs_summary.strip():
        needs_summary = fallback["needs_summary"]

    why_you_raw = data.get("why_you")
    why_you: dict[str, str] = {}
    for m in top_matches:
        opp_id = m["opportunity_id"]
        text = why_you_raw.get(opp_id) if isinstance(why_you_raw, dict) else None
        if not isinstance(text, str) or not text.strip():
            text = fallback["why_you"][opp_id]
        why_you[opp_id] = text.strip()

    return {"needs_summary": needs_summary.strip(), "why_you": why_you}


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/api/profile", response_model=ProfileResponse)
async def create_profile(
    file: UploadFile,
    interests: str = Form(""),
    availability: str = Form(""),
) -> ProfileResponse:
    content = await file.read()
    resume_text = extract_resume_text(file.filename or "", content)
    interests_list = parse_interests(interests)

    fallback = build_fallback_profile(resume_text, interests_list)
    user_prompt = build_profile_user_prompt(resume_text, interests_list, availability)
    raw = call_llm_json(PROFILE_SYSTEM_PROMPT, user_prompt, fallback)
    profile_fields = sanitize_profile_fields(raw, fallback)

    profile = {**profile_fields, "availability": availability}
    profile_id = store.save_profile(profile)

    return ProfileResponse(profile_id=profile_id, **profile)


@app.get("/api/matches/{profile_id}", response_model=MatchesResponse)
def get_matches(profile_id: str, scenario: str = "normal") -> MatchesResponse:
    if scenario not in ("normal", "surge"):
        raise HTTPException(status_code=400, detail="scenario must be 'normal' or 'surge'")

    profile = store.get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile not found")

    needs_payload = needs_service.get_needs_data()
    opportunities = load_active_opportunities()
    ranked = rank_opportunities(
        profile,
        opportunities,
        needs_payload["case_counts"],
        scenario,
        needs_payload["encampment_share"],
    )

    top_matches = ranked[:3]
    rest = ranked[3:]

    fallback_payload = _fallback_why_you_payload(profile, top_matches, needs_payload, scenario)
    if top_matches:
        user_prompt = _build_why_you_user_prompt(profile, top_matches, needs_payload, scenario)
        raw = call_llm_json(WHY_YOU_SYSTEM_PROMPT, user_prompt, fallback_payload, max_tokens=900)
        llm_payload = _sanitize_why_you_payload(raw, top_matches, fallback_payload)
    else:
        llm_payload = fallback_payload

    matches = []
    for m in top_matches:
        matches.append({**m, "why_you": llm_payload["why_you"].get(m["opportunity_id"])})
    for m in rest:
        matches.append({**m, "why_you": None})

    return MatchesResponse(matches=matches, scenario=scenario, needs_summary=llm_payload["needs_summary"])


@app.get("/api/needs", response_model=NeedsResponse)
def get_needs() -> NeedsResponse:
    needs_payload = needs_service.get_needs_data()
    return NeedsResponse(updated_at=needs_payload["updated_at"], neighborhoods=needs_payload["neighborhoods"])
