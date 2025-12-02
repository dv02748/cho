from __future__ import annotations

import time
from typing import Any, Dict

import requests
from requests import Session
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import ScraperConfig


class ChototClient:
    """HTTP client responsible for talking to the Chotot public API."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session: Session = Session()
        self.session.headers.update(
            {
                "user-agent": self.config.user_agent,
                "accept": "application/json,text/plain,*/*",
                "accept-language": "en-US,en;q=0.9",
                "origin": "https://www.chotot.com",
                "referer": "https://www.chotot.com/",
            }
        )

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def fetch_page(self, page: int, base_params: Dict[str, Any]) -> Dict[str, Any]:
        params = base_params.copy()
        params["page"] = page
        params.setdefault("limit", self.config.query.limit)

        response = self.session.get(
            self.config.base_url,
            params=params,
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        # Gentle delay to avoid hammering the remote API.
        time.sleep(self.config.delay_seconds)
        return response.json()
