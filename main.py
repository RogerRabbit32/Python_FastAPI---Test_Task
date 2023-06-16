import requests

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from schemas import RiddlesRequest, RiddlesResponse
from models import Base
from crud import save_riddles

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
    query_url = f"https://jservice.io/api/random?count={request.questions_num}"

    try:
        external_response = requests.get(query_url)
        riddles_to_save = external_response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    return save_riddles(db=db, riddles=riddles_to_save)
