from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from dependencies import get_current_user
from models import User
import crud


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.get("/")
async def get_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "login": current_user.login,
        "id": current_user.id,
        "user_name": current_user.username,
    }

@router.get("/quests")
async def get_user_quests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await crud.get_my_quests(db, current_user.id)
    return res

@router.get("/prigress")
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