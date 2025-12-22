from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "ai_assist_kbase")
    vllm_base_url: str = os.getenv("VLLM_BASE_URL", "http://localhost:8001/v1")
    vllm_api_key: str = os.getenv("VLLM_API_KEY", "")
    vllm_chat_model: str = os.getenv("VLLM_CHAT_MODEL", "AvitoTech/avibe")
    vllm_embed_model: str = os.getenv("VLLM_EMBED_MODEL", "AvitoTech/avibe")
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    rag_score_threshold: float = float(os.getenv("RAG_SCORE_THRESHOLD", "0"))
    max_history_messages: int = int(os.getenv("MAX_HISTORY_MESSAGES", "6"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are a helpful assistant. Use the provided context to answer the user."
        " If the context does not contain the answer, say you don't know.",
    )
