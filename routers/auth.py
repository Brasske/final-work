from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, TokenResponse
from auth_jwt import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=dict, 
            summary="Регистрация нового пользователя",
            description="Создаёт нового пользователя. Логин должен быть уникальным."
            )
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.login == user_data.login)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed = hash_password(user_data.password)
    user = User(
        login=user_data.login,
        hashed_password=hashed,
        username=user_data.username
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"status": "ok", "user_id": user.id}



@router.post("/login", response_model=TokenResponse, 
            summary="Аутентификация пользователя",
            description="Проверяет логин и пароль после чего возвращает JWT-токен."
             )
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.login == user_data.login)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

