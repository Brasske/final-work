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

@router.get(
    "/",
    summary="Получить список всех доступных квизов",
    description="Возвращает краткую информацию обо всех квизах в системе (без вопросов и ответов)."
)
async def get_quests(db: AsyncSession = Depends(get_db)):
    return await crud.get_quests(db)


@router.get(
    "/{quest_id}",
    summary="Получить квест по ID",
    description="Возвращает полную информацию о квизе, включая все вопросы и варианты ответов (без указания правильного ответа)."
)
async def get_quest(
    quest_id: int,
    db: AsyncSession = Depends(get_db)
):
    quest = await crud.get_quest(db, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Квиз не найден")
    return quest


@router.get(
    "/{quest_id}/{question_id}",
    summary="Получить один вопрос из квиза",
    description="Возвращает текст вопроса и список вариантов ответов (без указания правильного ответа)."
)
async def get_question(
    quest_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    question = await crud.get_question(db, quest_id, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    return question



@router.post(
    "/{quest_id}/{question_id}",
    summary="Отправить ответ на вопрос в квесте",
    description="""
    Проверяет, является ли выбранный ответ правильным.
    Если пользователь авторизован и ответ верен — сохраняет прогресс прохождения вопроса.
    Неавторизованные пользователи могут проверять ответы, но прогресс не сохраняется.
    """
)
async def passing_quest(
    quest_id: int,
    question_id: int,
    answer: AnswerGet,
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    question = await crud.get_question_with_correct_answer(db, quest_id, question_id)

    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    if question.correct_answer_id != answer.id:
        return {
            "is_correct": False,
            "correct_answer_id": question.correct_answer_id
        }

    saved = False
    if user:
        saved = await crud.record_correct_answer(db, user.id, quest_id, question_id)

    return {"is_correct": True, "saved": saved}


@router.post(
    "/",
    summary="Создать новый квиз",
    description="Создаёт квиз от имени текущего пользователя."
)
async def create_quest(
    quest: QuestCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    created = await crud.create_quest(db, quest, current_user)
    return {"id": created.id, "text": created.text}



@router.put(
    "/{quest_id}",
    summary="Обновить квиз",
    description="Полностью перезаписывает содержимое квеста (включая вопросы и ответы). Доступно только автору квиз."
)
async def change_quest(
    quest: QuestCreate,
    quest_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    updated = await crud.update_quest(db, quest_id, quest, current_user.id)
    return {"id": updated.id, "text": updated.text}


@router.delete(
    "/{quest_id}",
    summary="Удалить квиз",
    description="Удаляет квиз и все связанные с ним данные (вопросы, ответы, прогресс пользователей). Доступно только автору."
)
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

