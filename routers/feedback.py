from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from core.database import db
from core.logger import logger
from models.feedback import Feedback


router = APIRouter(prefix="/api", tags=["Feedback"])


@router.post("/feedback")
async def send_feedback(feedback: Feedback) -> dict[str, str]:
    """Persist user feedback for a chatbot response."""

    if not ObjectId.is_valid(feedback.message_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid message id")

    message = await db.messages.find_one({"_id": ObjectId(feedback.message_id)})
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    fb_data = {
        "message_id": feedback.message_id,
        "rating": feedback.rating,
        "comment": feedback.comment.strip() if feedback.comment else None,
        "created_at": datetime.now(tz=timezone.utc),
    }
    await db.feedbacks.insert_one(fb_data)
    logger.info("feedback_saved", extra={"message_id": feedback.message_id, "rating": feedback.rating})

    return {"status": "success", "message": "Feedback saved"}
