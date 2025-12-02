from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import requests
from requests import Response, Session

LOGGER = logging.getLogger(__name__)


class ChototClient:
    def __init__(
        self,
        base_url: str,
        user_agent: str | None = None,
        timeout: float = 10,
        delay_seconds: float = 1.0,
        session: Optional[Session] = None,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.delay_seconds = delay_seconds
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent
                or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        LOGGER.debug("Requesting %s with %s", self.base_url, params)
        response = self.session.get(self.base_url, params=params, timeout=self.timeout)
        self._handle_response(response)
        time.sleep(self.delay_seconds)
        return response.json()

    def _handle_response(self, response: Response) -> None:
        if response.status_code == 429:
            LOGGER.warning("Rate limited; sleeping before retry")
            time.sleep(self.delay_seconds * 2)
            response.raise_for_status()
        elif response.status_code >= 400:
            LOGGER.error("Request failed: %s", response.text)
            response.raise_for_status()


class DummyClient(ChototClient):
    def __init__(self, payload: Dict[str, Any]):
        super().__init__(base_url="http://example.com")
        self.payload = payload

    def get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.payload
