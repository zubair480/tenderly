import io
import logging

import pypdf

logger = logging.getLogger("tenderly.resume")

KNOWN_SKILLS = [
    "customer service", "teaching", "tutoring", "mentoring", "spanish", "mandarin",
    "cantonese", "translation", "driving", "logistics", "project management",
    "software engineering", "web development", "data analysis", "data science",
    "machine learning", "python", "javascript", "graphic design", "social media",
    "marketing", "physical labor", "gardening", "landscaping", "childcare",
    "counseling", "public speaking", "event planning", "fundraising", "grant writing",
    "bookkeeping", "accounting", "first aid", "nursing", "healthcare", "phlebotomy",
    "it support", "network administration", "leadership", "organization",
    "communication", "research", "writing", "cooking", "carpentry", "construction",
    "legal aid", "immigration law", "case management", "outreach", "sign language",
]

PROFILE_SYSTEM_PROMPT = (
    "You are an assistant that extracts a structured volunteer skill profile from a "
    "resume. Respond with ONLY a single valid JSON object and nothing else - no "
    "markdown fences, no commentary, no explanation. The JSON must have exactly "
    "these keys: "
    '"name" (string, the person\'s name if present else "Volunteer"), '
    '"skills" (array of 5-10 short lowercase skill strings), '
    '"experience_summary" (a one or two sentence plain-language summary), '
    '"causes" (array of 2-5 short cause strings such as "food security", "housing", '
    '"youth", "seniors", "climate", "health", "disability inclusion", '
    '"animal welfare", "immigrant support", "community safety", "education access", '
    '"digital literacy" - prefer causes implied by the resume and the volunteer\'s '
    "stated interests)."
)


def extract_resume_text(filename: str, content: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("pdf extraction failed: %s", exc)
            return ""
    try:
        return content.decode("utf-8", errors="ignore").strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("text decode failed: %s", exc)
        return ""


def build_profile_user_prompt(resume_text: str, interests: list[str], availability: str) -> str:
    truncated = resume_text[:6000]
    interests_str = ", ".join(interests) if interests else "(none specified)"
    return (
        f"Resume text:\n{truncated}\n\n"
        f"Volunteer's stated interests/causes: {interests_str}\n"
        f"Volunteer's stated availability: {availability}\n\n"
        "Extract the JSON profile now."
    )


def build_fallback_profile(resume_text: str, interests: list[str]) -> dict:
    text_lower = resume_text.lower()
    skills = [s for s in KNOWN_SKILLS if s in text_lower][:8]
    if not skills:
        skills = ["teamwork", "communication", "reliability"]

    causes = [c.strip() for c in interests if c.strip()] or ["community"]

    stripped = resume_text.strip().replace("\n", " ")
    if stripped:
        summary = stripped[:220] + ("..." if len(stripped) > 220 else "")
    else:
        summary = "Experienced volunteer ready to help San Francisco communities."

    return {
        "name": "Volunteer",
        "skills": skills,
        "experience_summary": summary,
        "causes": causes,
    }


def sanitize_profile_fields(data: dict, fallback: dict) -> dict:
    """Coerce a Gradient AI profile JSON to the expected types, field by field.

    An LLM can return the right keys with the wrong types (a string instead
    of a list, a missing key) even when json.loads succeeds. Falling back
    per-field keeps a partially-good LLM response instead of discarding it.
    """
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        name = fallback["name"]

    skills = data.get("skills")
    if not isinstance(skills, list) or not all(isinstance(s, str) for s in skills) or not skills:
        skills = fallback["skills"]

    experience_summary = data.get("experience_summary")
    if not isinstance(experience_summary, str) or not experience_summary.strip():
        experience_summary = fallback["experience_summary"]

    causes = data.get("causes")
    if not isinstance(causes, list) or not all(isinstance(c, str) for c in causes) or not causes:
        causes = fallback["causes"]

    return {
        "name": name.strip(),
        "skills": [s.strip().lower() for s in skills if s.strip()],
        "experience_summary": experience_summary.strip(),
        "causes": [c.strip().lower() for c in causes if c.strip()],
    }


def parse_interests(interests_raw: str) -> list[str]:
    """Accept either a JSON array string or a comma-separated string."""
    raw = (interests_raw or "").strip()
    if raw.startswith("["):
        import json

        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:  # noqa: BLE001
            pass
    return [x.strip() for x in raw.split(",") if x.strip()]
