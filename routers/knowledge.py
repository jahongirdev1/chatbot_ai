from fastapi import APIRouter, Depends
from core.auth import verify_admin
from core.database import db
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Knowledge"])

class KnowledgeItem(BaseModel):
    question_uz: str
    answer_uz: str
    question_ru: str
    answer_ru: str
    question_kz: str
    answer_kz: str
    category: str | None = None

@router.post("/knowledge", dependencies=[Depends(verify_admin)])
async def add_knowledge(item: KnowledgeItem):
    """Bazaga yangi savol-javob (3 tilda) qo‘shish"""
    await db.knowledge.insert_one(item.dict())
    return {"status": "success", "message": "Knowledge item added"}

@router.get("/knowledge", dependencies=[Depends(verify_admin)])
async def list_knowledge():
    """Admin uchun barcha savollar ro‘yxati"""
    items = await db.knowledge.find().to_list(100)
    return {"count": len(items), "data": items}
