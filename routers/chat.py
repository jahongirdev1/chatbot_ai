from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel

from core.database import db
from core.logger import logger
from models.message import Language, Message


class ChatResponse(BaseModel):
    answer: str
    source: Literal["knowledge_base", "not_found"]
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
        cursor = (
            db.knowledge.find(
                {"$text": {"$search": message.question}},
                projection={field_answer: 1, "score": {"$meta": "textScore"}},
            )
            .sort([("score", {"$meta": "textScore"})])
            .limit(1)
        )
        hits = await cursor.to_list(length=1)
        if hits:
            knowledge_doc = hits[0]
    except Exception:  # pragma: no cover - fallback if text search fails
        logger.exception("knowledge_text_search_failed", extra={"lang": lang.value})

    if not knowledge_doc:
        keywords = [word for word in re.findall(r"\w+", message.question) if len(word) > 2]
        if keywords:
            unique_keywords = list(dict.fromkeys(keywords))[:6]
            pattern = "|".join(re.escape(word) for word in unique_keywords)
            regex = {"$regex": pattern, "$options": "i"}
            knowledge_doc = await db.knowledge.find_one(
                {field_question: regex},
                projection={field_answer: 1},
            )

    answer = knowledge_doc.get(field_answer) if knowledge_doc else None
    source: Literal["knowledge_base", "not_found"] = "knowledge_base"

    if not answer:
        answer = (
            "ℹ️ Bu savol bo‘yicha bilimlar bazasida javob topilmadi. "
            "Iltimos, mavjud ma’lumotlarga mos savol bering."
        )
        source = "not_found"

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
