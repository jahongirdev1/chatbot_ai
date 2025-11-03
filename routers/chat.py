from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from ai_module import ask_ai
from core.database import db
from core.logger import logger
from models.message import Language, Message


class ChatResponse(BaseModel):
    answer: str
    source: Literal["knowledge_base", "ai"]
    message_id: str


router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask_bot(message: Message, lang: Language = Query(Language.uz)) -> ChatResponse:
    """Return an answer for the provided question in the requested language."""

    field_question = f"question_{lang.value}"
    field_answer = f"answer_{lang.value}"

    logger.info(
        "chat_question_received",
        extra={
            "user_id": message.user_id,
            "lang": lang.value,
        },
    )

    knowledge_doc = None
    try:
        knowledge_doc = await db.knowledge.find_one(
            {"$text": {"$search": f'"{message.question}"'}},
            projection={field_answer: 1},
        )
    except Exception:  # pragma: no cover - fallback if text search fails
        logger.exception("knowledge_text_search_failed", extra={"lang": lang.value})

    if not knowledge_doc:
        regex = {"$regex": re.escape(message.question), "$options": "i"}
        knowledge_doc = await db.knowledge.find_one(
            {field_question: regex},
            projection={field_answer: 1},
        )

    answer = knowledge_doc.get(field_answer) if knowledge_doc else None
    source: Literal["knowledge_base", "ai"] = "knowledge_base"

    if not answer:
        try:
            answer = await ask_ai(message.question, lang=lang.value)
            source = "ai"
        except Exception as exc:
            logger.exception(
                "ai_generation_failed",
                extra={"lang": lang.value, "user_id": message.user_id},
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to generate AI response.",
            ) from exc

    created_at = datetime.now(tz=timezone.utc)
    record = {
        "user_id": message.user_id,
        "question": message.question,
        "answer": answer,
        "lang": lang.value,
        "source": source,
        "created_at": created_at,
    }
    insert_result = await db.messages.insert_one(record)

    return ChatResponse(answer=answer, source=source, message_id=str(insert_result.inserted_id))
