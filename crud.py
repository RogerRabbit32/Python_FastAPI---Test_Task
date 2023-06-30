import requests
from typing import List

import dateutil.parser
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models import Riddle


def fetch_riddles(count: int) -> List:
    fetched_riddles = []
    ids_to_add = {}
    remaining_count = count
    successfully_added = 0

    while remaining_count > 0:
        current_count = min(remaining_count, 100)
        query_url = f"https://jservice.io/api/random?count={current_count}"
        try:
            external_response = requests.get(query_url)
            riddles = external_response.json()
            for riddle in riddles:
                if riddle["id"] in ids_to_add:
                    continue
                else:
                    fetched_riddles.append(riddle)
                    ids_to_add[riddle["id"]] = True
                    successfully_added += 1
            remaining_count -= successfully_added
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=502, detail=str(e))

    return fetched_riddles


def save_riddles(db: Session, riddles: List) -> Riddle:
    riddles_already_in_db = 0
    last_saved_riddle = None
    attempts = 3

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
            riddles_already_in_db += 1

    db.commit()

    print(f"---------!!!! Non-unique riddles: {riddles_already_in_db}!!!!-------------")
    while riddles_already_in_db != 0 and attempts != 0:
        new_riddles = fetch_riddles(riddles_already_in_db)
        for riddle in new_riddles:
            if riddles_already_in_db == 0:
                db.commit()
                return last_saved_riddle
            else:
                db_riddle = db.query(Riddle).filter_by(id=riddle["id"]).first()
                if db_riddle is None:
                    db_riddle = Riddle(
                        id=riddle["id"],
                        question=riddle["question"],
                        answer=riddle["answer"],
                        created_at=dateutil.parser.isoparse(riddle["created_at"])
                    )
                    db.add(db_riddle)
                    riddles_already_in_db -= 1
                    last_saved_riddle = riddle
                else:
                    continue
        db.commit()
        attempts -= 1

    print(f"---------!!!! Attempts left: {attempts}!!!!-------------")
    if riddles_already_in_db != 0 and attempts == 0:
        raise HTTPException(status_code=502, detail=f"Failed to add {len(riddles)} new unique riddles. "
                                                    f"Successfully added {len(riddles) - riddles_already_in_db}")

    return last_saved_riddle
