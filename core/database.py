from collections.abc import Mapping
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from core.config import settings
from core.logger import logger


client = AsyncIOMotorClient(settings.mongo_uri)
db: AsyncIOMotorDatabase = client[settings.mongo_db]


async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency that returns the configured MongoDB database."""

    return db


def serialize_document(document: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a MongoDB document into a JSON-serialisable dictionary."""

    serialised = dict(document)
    if serialised.get("_id") is not None:
        serialised["id"] = str(serialised.pop("_id"))
    return serialised


async def init_indexes() -> None:
    """Create the indexes required by the application collections."""

    try:
        await db.knowledge.create_index(
            [
                ("question_uz", "text"),
                ("question_ru", "text"),
                ("question_kz", "text"),
            ],
            name="knowledge_text_search",
            default_language="none",
        )
        await db.knowledge.create_index(
            [("category", 1)],
            name="knowledge_category_idx",
            sparse=True,
        )
        await db.messages.create_index(
            [("user_id", 1), ("created_at", -1)],
            name="messages_user_time_idx",
        )
        await db.feedbacks.create_index(
            [("message_id", 1), ("created_at", -1)],
            name="feedback_message_idx",
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to ensure MongoDB indexes", exc_info=exc)
