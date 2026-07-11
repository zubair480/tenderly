import io
import logging
import re

import pypdf

logger = logging.getLogger("tenderly.resume")

SKILLS_HEADINGS = {"skills", "skills & expertise", "technical skills", "core skills", "key skills"}
SUMMARY_HEADINGS = {"summary", "profile", "objective", "about", "about me"}
CAUSES_HEADINGS = {"causes", "causes i care about", "causes & interests", "interests"}

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


def _is_heading_line(line: str) -> bool:
    """A line is heading-like if it's one of our known section names, or
    generically short/all-caps the way resume section headers usually are
    (e.g. "EXPERIENCE", "EDUCATION") - used to know where a section ends.
    """
    stripped = line.strip().rstrip(":").strip()
    if not stripped:
        return False
    known = SKILLS_HEADINGS | SUMMARY_HEADINGS | CAUSES_HEADINGS
    if stripped.lower() in known:
        return True
    return len(stripped) <= 40 and stripped == stripped.upper() and any(c.isalpha() for c in stripped)


def _extract_section(lines: list[str], heading_names: set[str]) -> list[str]:
    """Return the lines following a heading matching one of `heading_names`.

    Handles two common resume formats: the heading alone on its own line
    with content below (e.g. "SKILLS\\nPython, SQL, ..."), and an inline
    "Label: content" line (e.g. "Skills: project coordination, Spanish").
    Returns [] if no such heading is found. Kept as separate lines (not
    pre-joined) so callers can decide whether to join with "\\n" (preserving
    per-line list boundaries) or " " (continuous prose).
    """
    for i, line in enumerate(lines):
        stripped = line.strip()
        line_as_heading = stripped.rstrip(":").strip()
        inline_label, _, inline_rest = stripped.partition(":")

        if line_as_heading.lower() in heading_names:
            collected = []
        elif inline_label.strip().lower() in heading_names and inline_rest.strip():
            collected = [inline_rest.strip()]
        else:
            continue

        for candidate in lines[i + 1 :]:
            if _is_heading_line(candidate):
                break
            if candidate.strip():
                collected.append(candidate.strip())
        return collected
    return []


def _split_list_section(text: str) -> list[str]:
    parts = re.split(r"[,;\n]", text)
    cleaned = []
    for part in parts:
        item = part.strip()
        if ":" in item:
            # Drop an inline sub-label like "Languages:" before the real
            # items, e.g. "Languages: Python" -> "Python".
            item = item.split(":", 1)[1].strip()
        item = item.strip(".").strip().lower()
        if item:
            cleaned.append(item)
    return cleaned


def _first_sentences(text: str, max_sentences: int = 2, max_len: int = 280) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    result = " ".join(sentences[:max_sentences]).strip()
    if len(result) > max_len:
        result = result[:max_len].rsplit(" ", 1)[0] + "..."
    return result


_NAME_WORD_RE = re.compile(r"^[A-Z][a-zA-Z'-]*\.?$")
_NAME_BLOCKLIST = {"resume", "cv", "curriculum", "vitae", "resumé", "résumé", "profile"}
_GENERIC_SKILLS_FALLBACK = ["teamwork", "communication", "reliability"]


def _join_natural(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _extract_name(resume_text: str) -> str | None:
    """Find a run of 2-4 Title-Case words at the start of an early line.

    A resume's first non-blank line is almost always the person's name, but
    pypdf frequently collapses an entire header (name, GitHub/LinkedIn
    links, phone, email) into a single line with no newlines - a very
    common resume layout. Requiring the *whole* line to look like a name
    fails on real PDFs; instead this only requires a name-shaped word run
    at the very start, and keeps scanning subsequent lines if the first
    doesn't yield one (e.g. a "Resume" banner line before the real name).

    Some PDFs go the opposite way: depending on how the source document
    justifies/kerns its header, pypdf can extract one word per line, with
    stray whitespace-only lines in between (e.g. "Muhammad\\n \\nZubair\\n
    \\nZafar\\n \\ngithub .com/..."). The per-line scan below never sees two
    name-words on the same line in that case, so first merge a leading run
    of bare single-word lines before falling back to the per-line check.
    """
    non_blank_lines = [line.strip() for line in resume_text.splitlines() if line.strip()]

    merged_words: list[str] = []
    for line in non_blank_lines[:8]:
        if len(merged_words) < 4 and _NAME_WORD_RE.match(line):
            merged_words.append(line)
        else:
            break
    if 1 < len(merged_words) <= 4 and not all(w.lower() in _NAME_BLOCKLIST for w in merged_words):
        return " ".join(merged_words)

    for line in resume_text.splitlines()[:5]:
        stripped = line.strip()
        if not stripped:
            continue

        # Cut at the first "|" or "," - common separators before contact
        # links/location in a one-line header - before walking words.
        first_segment = re.split(r"[|,]", stripped, maxsplit=1)[0].strip()

        name_words = []
        for word in first_segment.split():
            if len(name_words) >= 4 or not _NAME_WORD_RE.match(word):
                break
            name_words.append(word)

        if 1 < len(name_words) <= 4 and not all(w.lower() in _NAME_BLOCKLIST for w in name_words):
            return " ".join(name_words)
    return None


def build_fallback_profile(resume_text: str, interests: list[str]) -> dict:
    """Deterministic profile extraction used when Gradient AI is unavailable.

    Looks for common resume section headers (SKILLS, SUMMARY, CAUSES) first,
    since parsing those directly gives far better results than blind keyword
    scanning or raw-text truncation - falls back to those only when a resume
    has no recognizable section structure.
    """
    lines = resume_text.splitlines()

    name = _extract_name(resume_text) or "Volunteer"

    skills_lines = _extract_section(lines, SKILLS_HEADINGS)
    if skills_lines:
        # Joined with "\n" (not " ") so a per-line split still separates
        # multiple sub-categories, e.g. "Languages: Python, Java\nTools: Git"
        # doesn't fuse "Java" and "Tools:" together.
        skills = _split_list_section("\n".join(skills_lines))[:8]
    else:
        text_lower = resume_text.lower()
        skills = [s for s in KNOWN_SKILLS if s in text_lower][:8]
    if not skills:
        skills = list(_GENERIC_SKILLS_FALLBACK)

    summary_lines = _extract_section(lines, SUMMARY_HEADINGS)
    if summary_lines:
        summary = _first_sentences(" ".join(summary_lines))
    elif skills != _GENERIC_SKILLS_FALLBACK:
        # No SUMMARY/OBJECTIVE section - common for resumes that go straight
        # from contact info into EDUCATION/SKILLS (typical for early-career
        # and CS resumes). Synthesize from real extracted skills instead of
        # ever showing raw text, which can include contact info/links.
        summary = f"Brings hands-on experience in {_join_natural(skills[:3])}, ready to put those skills to work in the community."
    else:
        summary = "Experienced volunteer ready to help San Francisco communities."

    causes_lines = _extract_section(lines, CAUSES_HEADINGS)
    resume_causes = _split_list_section("\n".join(causes_lines)) if causes_lines else []
    causes = [c.strip() for c in interests if c.strip()] or list(resume_causes) or ["community"]
    existing_lower = {c.lower() for c in causes}
    for cause in resume_causes:
        if cause not in existing_lower:
            causes.append(cause)
            existing_lower.add(cause)

    return {
        "name": name,
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
