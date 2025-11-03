from pydantic import BaseModel
from typing import Literal


class Feedback(BaseModel):
    message_id: str  # bazadagi message `_id`
    rating: Literal["good", "bad"]  # foydalanuvchi bahosi
    comment: str | None = None
