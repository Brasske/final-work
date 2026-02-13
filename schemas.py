from pydantic import BaseModel
from typing import List, Optional

class AnswerCreate(BaseModel):
    text: str
    
class QuestionCreate(BaseModel):
    text: str
    answers: List[AnswerCreate]
    correct_answer_id: int

class QuestCreate(BaseModel):
    text: str
    questions: List[QuestionCreate]

class AnswerGet(BaseModel):
    id: int
class UserCreate(BaseModel):
    login: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    password: Optional[str] = None
    username: Optional[str] = None

class UserChange(BaseModel):
    username: str

class UserLogin(BaseModel):
    login: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"