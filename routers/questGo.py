from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from schemas import QuestCreate
import crud
from fastapi import HTTPException, status


router = APIRouter(
    prefix="/questsgo",
    tags=["QuestsGo"]
)

@router.get("/")
def get_quests(db: Session = Depends(get_db)):
    return crud.get_quests(db)

