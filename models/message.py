from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    user_id: str
    question: str
    answer: Optional[str] = None
