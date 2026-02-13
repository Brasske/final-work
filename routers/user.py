from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dependencies import get_current_user
from schemas import UserUpdate, UserResponse
from models import User
import crud


router = APIRouter(
    prefix="/user",
    tags=["User"]
)



@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_user = await crud.user_update(db, user_id, user_update)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user


@router.get(
        "/",
        summary="Получить данные профиля текущего пользователя",
        description="Возвращает основную информацию о залогиненном пользователе: логин, ID и имя."
        )
async def get_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "login": current_user.login,
        "id": current_user.id,
        "user_name": current_user.username,
    }

@router.get(
        "/quests",
        summary="Получить список квизов, созданных пользователем",
        description="Возвращает все квизы, текущего пользователя."
        )
async def get_user_quests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await crud.get_my_quests(db, current_user.id)
    return res

@router.get(
        "/progress",
        summary="Получить прогресс пользователя по пройденным квизам",
        description="""
        Возвращает список квизов, в которых пользователь завершил хотя бы один вопрос.
        Для каждого квиза указывается:
        - ID и текст квиза,
        - количество вопросов, на которые пользователь дал правильный ответ,
        - имя автора квиза.
        """
    )
async def user_quest_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rows = await crud.get_user_quest_progress(db, user.id)
    
    return [
        {
            "quest_id": quest.id,
            "quest_text": quest.text,
            "completed_questions": completed_count,
            "creator": quest.creator.username if quest.creator else None
        }
        for quest, completed_count in rows
    ]