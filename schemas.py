from datetime import datetime

from pydantic import BaseModel


class RiddlesRequest(BaseModel):
    questions_num: int


class RiddlesResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True
