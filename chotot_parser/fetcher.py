from __future__ import annotations

import logging
from typing import Iterable, List

from .client import ChototClient
from .config import ScraperConfig
from .models import AdRecord
from .parser import AdParser

LOGGER = logging.getLogger(__name__)


class AdFetcher:
    def __init__(self, client: ChototClient, config: ScraperConfig) -> None:
        self.client = client
        self.config = config

    def fetch_all(self) -> List[AdRecord]:
        listings: List[AdRecord] = []
        page = 0
        while True:
            if self.config.max_pages is not None and page >= self.config.max_pages:
                break
            params = self.config.build_params(page)
            payload = self.client.get(params)
            ads = list(AdParser.parse_listing_payload(payload))
            LOGGER.info("Fetched %d ads on page %d", len(ads), page + 1)
            listings.extend(ads)
            if not payload.get("has_more", False) or not ads:
                break
            page += 1
        return listings
