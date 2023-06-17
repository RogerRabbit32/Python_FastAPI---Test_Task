from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from schemas import RiddlesRequest, RiddlesResponse
from models import Base
from crud import fetch_riddles, save_riddles

Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/", response_model=RiddlesResponse)
async def get_new_questions(request: RiddlesRequest, db: Session = Depends(get_db)):
    riddles_to_save = fetch_riddles(request.questions_num)
    return save_riddles(db=db, riddles=riddles_to_save)
