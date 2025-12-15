from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user, get_current_user_optional
from schemas import QuestCreate, AnswerGet
import crud
from models import User



router = APIRouter(
    prefix="/quests",
    tags=["Quests"]
)

@router.get("/")
async def get_quests(db: AsyncSession = Depends(get_db)):
    return await crud.get_quests(db)


@router.get("/{quest_id}")
async def get_quest(quest_id: int, db: AsyncSession = Depends(get_db)):
    quest = await crud.get_quest(db, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    return quest


@router.get("/{quest_id}/{question_id}")
async def get_question(
    quest_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    question = await crud.get_question(db, quest_id, question_id)
    return question



@router.post("/{quest_id}/{question_id}")
async def passing_quest(
    quest_id: int,
    question_id: int,
    answer: AnswerGet,
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    question = await crud.get_question(db, quest_id, question_id)

    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    if question.correct_answer_id != answer.id:
        return {
            "is_correct": False,
            "correct_answer_id": question.correct_answer_id
        }

    return {"is_correct": True}


@router.post("/")
async def create_quest_route(
    quest: QuestCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    created = await crud.create_quest(db, quest, current_user)
    return {"id": created.id, "text": created.text}



@router.delete("/{quest_id}")
async def delete_quest(
    quest_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    res = await crud.delete_quest(
        db=db,
        quest_id=quest_id,
        user_id=current_user.id
    )
    return res


