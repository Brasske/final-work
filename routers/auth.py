from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, TokenResponse
from auth_jwt import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=dict)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.login == user_data.login).first()
    if existing:
        raise HTTPException(400, "User already exists")

    hashed = hash_password(user_data.password)
    user = User(login=user_data.login, hashed_password=hashed, username=user_data.username)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "ok", "user_id": user.id}


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == user_data.login).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)
