import datetime
import json
import logging
import time

import httpx

from app.config import NEEDS_CACHE_TTL_SECONDS, NEEDS_SNAPSHOT_PATH, SOCRATA_BASE_URL
from app.matching import normalize_neighborhood_key

logger = logging.getLogger("tenderly.needs")

ENCAMPMENT_SERVICE_NAMES = {"encampments", "encampment"}
TOP_N_NEIGHBORHOODS = 8
TOP_CATEGORIES_PER_NEIGHBORHOOD = 3

_cache: dict = {"payload": None, "fetched_at": 0.0}


def _seven_days_ago_iso() -> str:
    dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _aggregate_rows(rows: list[dict]) -> dict:
    case_counts: dict[str, int] = {}
    display_names: dict[str, str] = {}
    category_counts: dict[str, dict[str, int]] = {}
    encampment_counts: dict[str, int] = {}

    for row in rows:
        raw_name = (row.get("neighborhoods_sffind_boundaries") or "").strip()
        if not raw_name:
            continue
        key = normalize_neighborhood_key(raw_name)
        case_counts[key] = case_counts.get(key, 0) + 1

        existing = display_names.get(key)
        if existing is None or (existing.isupper() and not raw_name.isupper()):
            display_names[key] = raw_name.title() if raw_name.isupper() else raw_name

        category = (row.get("service_name") or "Other").strip()
        cat_map = category_counts.setdefault(key, {})
        cat_map[category] = cat_map.get(category, 0) + 1
        if category.lower() in ENCAMPMENT_SERVICE_NAMES:
            encampment_counts[key] = encampment_counts.get(key, 0) + 1

    encampment_share = {
        key: round(encampment_counts.get(key, 0) / count, 4) for key, count in case_counts.items()
    }

    top_keys = sorted(case_counts, key=lambda k: -case_counts[k])[:TOP_N_NEIGHBORHOODS]
    neighborhoods = []
    for key in top_keys:
        cats_sorted = sorted(category_counts.get(key, {}).items(), key=lambda kv: -kv[1])
        top_categories = [c for c, _ in cats_sorted[:TOP_CATEGORIES_PER_NEIGHBORHOOD]]
        neighborhoods.append(
            {
                "name": display_names.get(key, key.title()),
                "case_count": case_counts[key],
                "top_categories": top_categories,
            }
        )

    return {"neighborhoods": neighborhoods, "case_counts": case_counts, "encampment_share": encampment_share}


def _fetch_live() -> dict:
    since = _seven_days_ago_iso()
    params = {
        "$select": "neighborhoods_sffind_boundaries,service_name",
        "$where": f"requested_datetime > '{since}'",
        "$limit": "500",
    }
    with httpx.Client(timeout=8.0) as client:
        resp = client.get(SOCRATA_BASE_URL, params=params)
        resp.raise_for_status()
        rows = resp.json()
    return _aggregate_rows(rows)


def _load_snapshot() -> dict:
    with open(NEEDS_SNAPSHOT_PATH, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    case_counts: dict[str, int] = {}
    encampment_share: dict[str, float] = {}
    neighborhoods = []
    for n in snapshot.get("neighborhoods", []):
        key = normalize_neighborhood_key(n["name"])
        case_counts[key] = n.get("case_count", 0)
        encampment_share[key] = n.get("encampment_share", 0.0)
        neighborhoods.append(
            {
                "name": n["name"],
                "case_count": n.get("case_count", 0),
                "top_categories": n.get("top_categories", []),
            }
        )

    return {"neighborhoods": neighborhoods, "case_counts": case_counts, "encampment_share": encampment_share}


def get_needs_data(force_refresh: bool = False) -> dict:
    """Returns aggregated needs data, cached in memory for NEEDS_CACHE_TTL_SECONDS.

    Shape: {"updated_at", "neighborhoods", "case_counts", "encampment_share", "source"}.
    `neighborhoods` is exactly the NeedsResponse shape; `case_counts` and
    `encampment_share` are internal signals for the matching engine, keyed by
    `matching.normalize_neighborhood_key`.
    """
    now = time.monotonic()
    cached = _cache["payload"]
    if not force_refresh and cached is not None and (now - _cache["fetched_at"]) < NEEDS_CACHE_TTL_SECONDS:
        return cached

    try:
        aggregated = _fetch_live()
        source = "socrata_live"
    except Exception as exc:  # noqa: BLE001 - Socrata being down must never break /api/matches
        logger.warning("Socrata fetch failed, falling back to bundled snapshot: %s", exc)
        aggregated = _load_snapshot()
        source = "bundled_snapshot"

    payload = {
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "neighborhoods": aggregated["neighborhoods"],
        "case_counts": aggregated["case_counts"],
        "encampment_share": aggregated["encampment_share"],
        "source": source,
    }
    _cache["payload"] = payload
    _cache["fetched_at"] = now
    return payload
