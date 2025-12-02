from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from .client import ChototClient
from .config import ScraperConfig
from .models import Listing
from .parser import parse_ads

logger = logging.getLogger(__name__)


class ChototScraper:
    """Orchestrates pagination, parsing, and aggregation of listing data."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.client = ChototClient(config)

    def scrape(self, max_pages: Optional[int] = None) -> List[Listing]:
        collected: List[Listing] = []
        params = self.config.query.as_params()
        limit = params.get("limit", self.config.query.limit)
        page = 1
        pages_cap = max_pages or self.config.max_pages

        while True:
            logger.info("Fetching page %s with params %s", page, params)
            payload = self.client.fetch_page(page=page, base_params=params)
            page_ads = parse_ads(payload, self.config)
            collected.extend(page_ads)

            total = payload.get("total") or payload.get("total_ads")
            if not page_ads:
                logger.info("No ads on page %s; stopping.", page)
                break

            if pages_cap and page >= pages_cap:
                logger.info("Reached page cap %s", pages_cap)
                break

            if total and len(collected) >= total:
                logger.info("Reached total ads %s", total)
                break

            expected_pages = None
            if total and limit:
                expected_pages = (int(total) + int(limit) - 1) // int(limit)

            page += 1
            if expected_pages and page > expected_pages:
                break

        return collected

    @staticmethod
    def dump_to_json(listings: Iterable[Listing], path: str) -> None:
        import json

        with open(path, "w", encoding="utf-8") as handle:
            json.dump([listing.as_dict() for listing in listings], handle, ensure_ascii=False, indent=2)

    @staticmethod
    def dump_to_csv(listings: Iterable[Listing], path: str) -> None:
        import csv

        rows = [listing.as_dict() for listing in listings]
        if not rows:
            return

        fieldnames = list(rows[0].keys())
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
