from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import requests

from .config import AppConfig

logger = logging.getLogger(__name__)


class VLLMClient:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def _headers(self) -> Dict[str, str]:
        if self._config.vllm_api_key:
            return {"Authorization": f"Bearer {self._config.vllm_api_key}"}
        return {}

    def embed(self, text: str) -> List[float]:
        url = f"{self._config.vllm_base_url}/embeddings"
        payload = {"model": self._config.vllm_embed_model, "input": text}
        response = requests.post(
            url, json=payload, headers=self._headers(), timeout=self._config.request_timeout
        )
        response.raise_for_status()
        data = response.json()
        embedding = data.get("data", [{}])[0].get("embedding")
        if not embedding:
            raise ValueError("Embedding response missing data")
        return embedding

    def chat(self, messages: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
        url = f"{self._config.vllm_base_url}/chat/completions"
        payload = {
            "model": self._config.vllm_chat_model,
            "messages": messages,
            "temperature": 0.2,
        }
        response = requests.post(
            url, json=payload, headers=self._headers(), timeout=self._config.request_timeout
        )
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("Chat response missing choices")
        content = choices[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        logger.debug("Chat usage: %s", usage)
        return content, usage
