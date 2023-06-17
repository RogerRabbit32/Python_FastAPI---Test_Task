import requests
from typing import List, Union

import dateutil.parser
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models import Riddle


def fetch_riddles(count: int) -> List:
    fetched_riddles = []
    remaining_count = count

    while remaining_count > 0:
        current_count = min(remaining_count, 100)
        query_url = f"https://jservice.io/api/random?count={current_count}"
        try:
            external_response = requests.get(query_url)
            riddles = external_response.json()
            fetched_riddles.extend(riddles)
            remaining_count -= current_count
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=502, detail=str(e))

    return fetched_riddles


def save_riddles(db: Session, riddles: List) -> Union[int, Riddle]:
    non_unique_riddles = 0
    attempts = 3
    last_saved_riddle = None

    for riddle in riddles:
        db_riddle = db.query(Riddle).filter_by(id=riddle["id"]).first()
        if db_riddle is None:
            db_riddle = Riddle(
                id=riddle["id"],
                question=riddle["question"],
                answer=riddle["answer"],
                created_at=dateutil.parser.isoparse(riddle["created_at"])
            )
            db.add(db_riddle)
            last_saved_riddle = riddle
        else:
            non_unique_riddles += 1

    while non_unique_riddles != 0 and attempts != 0:
        new_riddles = fetch_riddles(non_unique_riddles * 2)
        for riddle in new_riddles:
            if non_unique_riddles == 0:
                db.commit()
                return last_saved_riddle
            db_riddle = db.query(Riddle).filter_by(id=riddle["id"]).first()
            if db_riddle is None:
                db_riddle = Riddle(
                    id=riddle["id"],
                    question=riddle["question"],
                    answer=riddle["answer"],
                    created_at=dateutil.parser.isoparse(riddle["created_at"])
                )
                db.add(db_riddle)
                non_unique_riddles -= 1
                last_saved_riddle = riddle
            else:
                continue
        attempts -= 1

    if non_unique_riddles != 0 and attempts == 0:
        raise HTTPException(status_code=502, detail="Failed to fetch the requested amount of new riddles")

    print(f"---------!!!!{attempts}!!!!-------------")
    db.commit()
    return last_saved_riddle
