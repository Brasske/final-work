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

class UserCreate(BaseModel):
    login: str
    password: str
    username: str

class UserLogin(BaseModel):
    login: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"