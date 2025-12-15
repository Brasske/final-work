from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect
from database import get_db
from dependencies import get_current_user
from models import User


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
        "comlite_questions": current_user.complite_questions
    }

