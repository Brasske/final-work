from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, get_current_user_optional
from schemas import QuestCreate, AnswerGet
import crud
from models import User
from fastapi import HTTPException, status


router = APIRouter(
    prefix="/quests",
    tags=["Quests"]
)

@router.get("/")
def get_quests(db: Session = Depends(get_db)):
    return crud.get_quests(db)

@router.get("/{quest_id}")
def get_quest(quest_id: int, db: Session = Depends(get_db)):
    quest = crud.get_quest(db, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    return quest

@router.get("/{quest_id}/{question_id}")
def get_question(quest_id: int, question_id: int, db: Session = Depends(get_db)):
    question = crud.get_question(db, quest_id, question_id)
    
    return question

@router.post("/{quest_id}/{question_id}")
def passing_quest(
    quest_id: int,
    question_id: int,
    answer: AnswerGet,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
    ):

    question = crud.get_question(db, quest_id, question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    if (question.correct_answer_id != answer.id):
        return {"is_correct": False, "correct_answer_id": question.correct_answer_id}
    return {"is_correct": True}

@router.post("/")
def create_quest_route(
        quest: QuestCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    created = crud.create_quest(db, quest, current_user)
    return {"id": created.id, "text": created.text}


@router.delete("/{quest_id}")
def delete_quest(
    quest_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    res = crud.delete_quest(db=db, quest_id=quest_id, user_id=current_user.id)
    return res

