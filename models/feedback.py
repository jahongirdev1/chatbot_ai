from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    message_id: str = Field(..., min_length=1)
    rating: Literal["good", "bad"]
    comment: str | None = Field(default=None, max_length=512)
