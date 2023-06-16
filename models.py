from sqlalchemy import Column, Integer, String, Date
from database import Base


class Riddle(Base):
    __tablename__ = "riddles"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answer = Column(String)
    created_at = Column(Date)
