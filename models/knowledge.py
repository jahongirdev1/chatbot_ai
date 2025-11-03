from __future__ import annotations

from pydantic import BaseModel, Field


class KnowledgeItem(BaseModel):
    question_uz: str = Field(..., min_length=1, max_length=1024)
    answer_uz: str = Field(..., min_length=1)
    question_ru: str = Field(..., min_length=1, max_length=1024)
    answer_ru: str = Field(..., min_length=1)
    question_kz: str = Field(..., min_length=1, max_length=1024)
    answer_kz: str = Field(..., min_length=1)
    category: str | None = Field(default=None, max_length=128)


class KnowledgeResponse(KnowledgeItem):
    id: str = Field(..., description="MongoDB document identifier")


class KnowledgeListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[KnowledgeResponse]
