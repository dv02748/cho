from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List

import requests

from .config import AppConfig

logger = logging.getLogger(__name__)


class QdrantClient:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def upsert(self, points: Iterable[Dict[str, Any]]) -> None:
        url = (
            f"{self._config.qdrant_url}/collections/"
            f"{self._config.qdrant_collection}/points?wait=true"
        )
        payload = {"points": list(points)}
        response = requests.put(url, json=payload, timeout=self._config.request_timeout)
        response.raise_for_status()
        logger.info("Upserted %s points into %s", len(payload["points"]), self._config.qdrant_collection)

    def search(self, vector: List[float], limit: int) -> List[Dict[str, Any]]:
        url = (
            f"{self._config.qdrant_url}/collections/"
            f"{self._config.qdrant_collection}/points/search"
        )
        payload = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
        }
        if self._config.rag_score_threshold > 0:
            payload["score_threshold"] = self._config.rag_score_threshold
        response = requests.post(url, json=payload, timeout=self._config.request_timeout)
        response.raise_for_status()
        return response.json().get("result", [])
