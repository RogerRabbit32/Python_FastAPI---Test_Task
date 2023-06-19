from datetime import datetime

from pydantic import BaseModel, Field


class RiddlesRequest(BaseModel):
    questions_num: int = Field(..., gt=0, le=1000)


class RiddlesResponse(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True
