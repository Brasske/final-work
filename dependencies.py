from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from auth_jwt import decode_access_token


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    user_id = decode_access_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

security_optional = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_optional),
    db: AsyncSession = Depends(get_db)
):
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        user_id = decode_access_token(token)
    except Exception:
        return None

    if not user_id:
        return None

    result = await db.execute(
        select(User).where(User.id == int(user_id))
    )
    return result.scalar_one_or_none()

