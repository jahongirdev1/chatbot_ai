from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Language(str, Enum):
    uz = "uz"
    ru = "ru"
    kz = "kz"


class Message(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    question: str = Field(..., min_length=1, max_length=2048)
    answer: str | None = Field(default=None)
