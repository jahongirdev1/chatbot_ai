from fastapi import APIRouter
from models.feedback import Feedback
from core.database import db
from bson import ObjectId

router = APIRouter(prefix="/api", tags=["Feedback"])

@router.post("/feedback")
async def send_feedback(feedback: Feedback):
    """
    Foydalanuvchi javobdan mamnun yoki yo‘qligini bildiradi.
    """
    msg = await db.messages.find_one({"_id": ObjectId(feedback.message_id)})
    if not msg:
        return {"status": "error", "message": "Message not found"}

    # feedbackni bazaga yozamiz
    fb_data = {
        "message_id": feedback.message_id,
        "rating": feedback.rating,
        "comment": feedback.comment
    }
    await db.feedbacks.insert_one(fb_data)

    return {"status": "success", "message": "Feedback saved"}
