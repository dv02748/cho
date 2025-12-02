from __future__ import annotations

import logging
from typing import List

from .client import ChototClient
from .config import ScraperConfig
from .fetcher import AdFetcher
from .models import AdRecord
from .storage import LocalStorage

LOGGER = logging.getLogger(__name__)


class ScraperService:
    def __init__(
        self,
        config: ScraperConfig,
        client: ChototClient | None = None,
        storage: LocalStorage | None = None,
    ) -> None:
        self.config = config
        self.client = client or ChototClient(config.base_url, delay_seconds=config.delay_seconds)
        self.storage = storage or LocalStorage()
        self.fetcher = AdFetcher(self.client, self.config)

    def refresh(self) -> List[AdRecord]:
        LOGGER.info("Starting scrape for city=%s category=%s", self.config.city, self.config.category_id)
        ads = self.fetcher.fetch_all()
        self.storage.save(ads)
        LOGGER.info("Saved %d ads", len(ads))
        return ads

    def load_cached(self) -> List[AdRecord]:
        return self.storage.load()
