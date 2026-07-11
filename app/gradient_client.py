import json
import logging
import time

from openai import OpenAI

from app.config import GRADIENT_API_KEY, GRADIENT_BASE_URL, GRADIENT_MODEL

logger = logging.getLogger("tenderly.gradient")

_clients: dict[float, OpenAI] = {}


def get_client(timeout_seconds: float = 12.0) -> OpenAI:
    """Reuse clients by timeout profile so batch jobs can allow more time."""
    if timeout_seconds not in _clients:
        _clients[timeout_seconds] = OpenAI(
            api_key=GRADIENT_API_KEY or "missing-key",
            base_url=GRADIENT_BASE_URL,
            timeout=timeout_seconds,
            max_retries=0,
        )
    return _clients[timeout_seconds]


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    fallback: dict,
    max_tokens: int = 800,
    temperature: float = 0.4,
    timeout_seconds: float = 12.0,
    model: str | None = None,
    json_mode: bool = False,
) -> dict:
    """Call Gradient AI expecting a pure JSON object back.

    Strips markdown fences, retries once on any failure (API error or bad
    JSON), and returns `fallback` on a second failure so the demo never 500s.
    """
    client = get_client(timeout_seconds)

    def _attempt() -> dict:
        start = time.monotonic()
        request_kwargs = {}
        if json_mode:
            request_kwargs["response_format"] = {"type": "json_object"}

        resp = client.chat.completions.create(
            model=model or GRADIENT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **request_kwargs,
        )
        latency = time.monotonic() - start
        content = resp.choices[0].message.content or ""
        logger.info("gradient call latency=%.2fs model=%s", latency, model or GRADIENT_MODEL)
        cleaned = _strip_fences(content)
        return json.loads(cleaned)

    for attempt in (1, 2):
        try:
            return _attempt()
        except Exception as exc:  # noqa: BLE001 - never let a bad LLM call 500 the demo
            logger.warning("gradient call failed (attempt %d/2): %s", attempt, exc)

    logger.error("gradient call failed twice, using fallback")
    return fallback
