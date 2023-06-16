from typing import List

import dateutil.parser
from sqlalchemy.orm import Session

from models import Riddle


def save_riddles(db: Session, riddles: List):
    for riddle in riddles:
        db_riddle = Riddle(
            id=riddle["id"],
            question=riddle["question"],
            answer=riddle["answer"],
            created_at=dateutil.parser.isoparse(riddle["created_at"])
        )
        db.add(db_riddle)
    db.commit()
    return riddles[-1]
