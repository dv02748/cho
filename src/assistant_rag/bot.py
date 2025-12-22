from __future__ import annotations

import asyncio
import logging
import os
from typing import Dict

import httpx
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

router = Router()
conversation_cache: Dict[int, str] = {}


@router.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer("Привет! Напишите ваш вопрос, и я передам его ассистенту.")


@router.message()
async def on_message(message: Message) -> None:
    if not BOT_TOKEN:
        await message.answer("BOT_TOKEN is not configured.")
        return

    conversation_id = conversation_cache.get(message.chat.id)
    payload = {
        "user_id": str(message.from_user.id) if message.from_user else None,
        "chat_id": str(message.chat.id),
        "message": message.text or "",
        "conversation_id": conversation_id,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(f"{BACKEND_URL}/chat", json=payload)
        response.raise_for_status()
        data = response.json()

    conversation_cache[message.chat.id] = data.get("conversation_id", conversation_id)
    await message.answer(data.get("reply", ""))


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required")
    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
