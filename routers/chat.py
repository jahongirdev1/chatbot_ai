from fastapi import APIRouter, Query
from models.message import Message
from ai_module import ask_ai
from core.database import db
from core.logger import logger

router = APIRouter(prefix="/api", tags=["Chat"])

@router.post("/ask")
async def ask_bot(
    message: Message,
    lang: str = Query("uz", enum=["uz", "ru", "kz"])
):
    """
    1️⃣ Bazadan kerakli tildagi savolni qidiradi
    2️⃣ Topilmasa AI'dan shu tilda javob oladi
    """
    logger.info(f"🧠 {message.user_id} → {message.question} ({lang})")

    field_question = f"question_{lang}"
    field_answer = f"answer_{lang}"

    result = await db.knowledge.find_one({
        field_question: {"$regex": message.question, "$options": "i"}
    })

    if result and result.get(field_answer):
        answer = result[field_answer]
        source = "knowledge_base"
    else:
        answer = await ask_ai(message.question, lang=lang)
        source = "ai"

    await db.messages.insert_one({
        "user_id": message.user_id,
        "question": message.question,
        "answer": answer,
        "lang": lang,
        "source": source
    })

    return {"answer": answer, "source": source}
