from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import AppConfig
from .service import AssistantService

logger = logging.getLogger(__name__)

app = FastAPI(title="Assistant RAG Service", version="1.0.0")
config = AppConfig()
service = AssistantService(config)


class ChatRequest(BaseModel):
    user_id: Optional[str] = None
    chat_id: Optional[str] = None
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    sources: List[Dict[str, Any]]
    conversation_id: str
    tokens: Dict[str, Any]


class IngestDocument(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None


class IngestRequest(BaseModel):
    documents: List[IngestDocument]


class IngestResponse(BaseModel):
    ingested: int


class FeedbackRequest(BaseModel):
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    try:
        ingested = service.ingest([doc.model_dump() for doc in req.documents])
    except Exception as exc:  # pragma: no cover - runtime guard
        logger.exception("Ingest failed: %s", exc)
        raise HTTPException(status_code=500, detail="Ingest failed")
    return IngestResponse(ingested=ingested)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    conversation_id = req.conversation_id or str(uuid.uuid4())
    try:
        reply, sources, tokens = service.chat(
            conversation_id=conversation_id,
            message=req.message,
            user_id=req.user_id,
            chat_id=req.chat_id,
        )
    except Exception as exc:  # pragma: no cover - runtime guard
        logger.exception("Chat failed: %s", exc)
        raise HTTPException(status_code=500, detail="Chat failed")

    return ChatResponse(
        reply=reply,
        sources=sources,
        conversation_id=conversation_id,
        tokens=tokens,
    )


@app.post("/feedback")
def feedback(req: FeedbackRequest) -> Dict[str, str]:
    logger.info("Feedback: %s", req.model_dump())
    return {"status": "received"}
