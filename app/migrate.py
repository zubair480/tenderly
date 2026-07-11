"""Apply the opportunity catalog schema and seed the curated demo catalog."""

import logging

from app.opportunity_repository import ensure_schema, seed_catalog_if_empty

logging.basicConfig(level=logging.INFO)


def main() -> None:
    ensure_schema()
    seeded = seed_catalog_if_empty()
    logging.getLogger("tenderly.migrate").info("opportunity catalog schema ready; seeded=%d", seeded)


if __name__ == "__main__":
    main()
