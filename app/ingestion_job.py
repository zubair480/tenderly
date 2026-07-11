"""Entrypoint for the six-hour DigitalOcean opportunity ingestion job."""

import hashlib
import logging

from app.config import OPPORTUNITY_INGESTION_ENABLED, OPPORTUNITY_PARSER_PATH, OPPORTUNITY_SOURCES_PATH
from app.opportunity_ingestion import enabled_sources, fetch_source, load_json_file, parse_and_classify
from app.opportunity_repository import ensure_schema, finish_import, reconcile_source, save_import_records, create_import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tenderly.ingestion_job")


def run() -> dict[str, int]:
    """Run every configured source once and return useful, log-friendly totals."""
    if not OPPORTUNITY_INGESTION_ENABLED:
        logger.info("opportunity ingestion is disabled; set OPPORTUNITY_INGESTION_ENABLED=true to activate it")
        return {"sources": 0, "promoted": 0, "unchanged": 0, "failed": 0}

    ensure_schema()
    sources = [
        source
        for source in enabled_sources(load_json_file(OPPORTUNITY_SOURCES_PATH))
        if source.get("type") in {"html_page", "json_api"}
    ]
    parser_config = load_json_file(OPPORTUNITY_PARSER_PATH)
    totals = {"sources": 0, "promoted": 0, "unchanged": 0, "failed": 0}

    for source in sources:
        totals["sources"] += 1
        import_id = None
        try:
            content = fetch_source(source)
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            import_id = create_import(source["id"], source["url"], content_hash, content)
            if import_id is None:
                totals["unchanged"] += 1
                logger.info("source=%s unchanged", source["id"])
                continue

            approved, pending, valid = parse_and_classify(content, source, parser_config)
            promoted = save_import_records(import_id, approved, pending)
            finish_import(import_id, "parsed", parsed_records=valid)
            if valid:
                reconcile_source(source["id"], [record["source_key"] for record in valid])
            totals["promoted"] += promoted
            logger.info(
                "source=%s parsed=%d promoted=%d pending_review=%d",
                source["id"], len(valid), promoted, len(pending),
            )
        except Exception as exc:  # One partner source must not stop the other sources.
            totals["failed"] += 1
            logger.exception("source=%s import failed", source.get("id"))
            if import_id:
                finish_import(import_id, "failed", error=str(exc)[:1_000])

    return totals


def main() -> None:
    logger.info("opportunity import complete: %s", run())


if __name__ == "__main__":
    main()
