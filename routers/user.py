from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from schemas import QuestCreate
import crud
from fastapi import HTTPException
from models import User
from schemas import UserLogin, TokenResponse
from auth_jwt import verify_password, create_access_token


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.get("/")
def create_quest_route(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    res = {
        "login": current_user.login,
        "id": current_user.id,
        "user_name": current_user.username
    }
    return res

# @router.put("/")
# def change_username(
#     db: Session = Depends(get)
# ):
