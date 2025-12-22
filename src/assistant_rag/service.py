from __future__ import annotations

import logging
import uuid
from typing import Dict, List, Tuple

from .config import AppConfig
from .qdrant import QdrantClient
from .store import ConversationStore
from .vllm import VLLMClient

logger = logging.getLogger(__name__)


class AssistantService:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._qdrant = QdrantClient(config)
        self._vllm = VLLMClient(config)
        self._store = ConversationStore(config.max_history_messages)

    def ingest(self, documents: List[Dict[str, object]]) -> int:
        points = []
        for document in documents:
            text = str(document.get("text", "")).strip()
            if not text:
                continue
            metadata = document.get("metadata", {}) or {}
            embedding = self._vllm.embed(text)
            point_id = document.get("id") or str(uuid.uuid4())
            payload = {**metadata, "text": text}
            points.append({"id": point_id, "vector": embedding, "payload": payload})

        if points:
            self._qdrant.upsert(points)
        return len(points)

    def chat(
        self, conversation_id: str, message: str, user_id: str | None = None, chat_id: str | None = None
    ) -> Tuple[str, List[Dict[str, object]], Dict[str, object]]:
        embedding = self._vllm.embed(message)
        hits = self._qdrant.search(embedding, self._config.rag_top_k)
        context_blocks: List[str] = []
        sources: List[Dict[str, object]] = []
        for hit in hits:
            payload = hit.get("payload", {})
            text = str(payload.get("text", "")).strip()
            if text:
                context_blocks.append(text)
            sources.append(
                {
                    "source": payload.get("source"),
                    "file_name": payload.get("file_name"),
                    "page": payload.get("page"),
                    "chunk_id": payload.get("chunk_id"),
                    "created_at": payload.get("created_at"),
                    "score": hit.get("score"),
                }
            )

        context = "\n\n".join(context_blocks)
        system_prompt = self._config.system_prompt
        if context:
            system_prompt = f"{system_prompt}\n\nContext:\n{context}"

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self._store.history(conversation_id))
        messages.append({"role": "user", "content": message})

        reply, usage = self._vllm.chat(messages)
        self._store.append(conversation_id, "user", message)
        self._store.append(conversation_id, "assistant", reply)

        tokens = {
            "input": usage.get("prompt_tokens"),
            "output": usage.get("completion_tokens"),
            "total": usage.get("total_tokens"),
        }
        metadata = {"user_id": user_id, "chat_id": chat_id}
        logger.info("Generated reply for conversation %s", conversation_id)
        return reply, sources, {**tokens, **metadata}
