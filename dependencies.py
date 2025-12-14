from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth_jwt import decode_access_token

from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth_jwt import decode_access_token

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials   

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials 
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


security_optional = HTTPBearer(auto_error=False)

def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_optional),
    db: Session = Depends(get_db)
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

    return db.query(User).filter(User.id == int(user_id)).first()