from sqlalchemy.orm import Session
from models import Quest, Question, Answer, User
from schemas import QuestCreate
from fastapi import HTTPException


# def change_quest(db: Session, quest_data: QuestCreate, user):
#     quest = db.query(Quest).filter(Quest.id == quest_data.id)

def delete_quest(db: Session, quest_id, user_id):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")

    if quest.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Пользователь не владелец квиза")
    
    db.delete(quest)
    db.commit()

    return {"status":"ok"}

def create_quest(db: Session, quest_data: QuestCreate, user):
    quest = Quest(
        text=quest_data.text,
        creator_id=user.id
    )

    db.add(quest)
    db.flush()

    for q in quest_data.questions:
        question = Question(text=q.text, quest=quest)
        db.add(question)
        db.flush()

        answers = []
        for a in q.answers:
            obj = Answer(text=a.text, question=question)
            db.add(obj)
            answers.append(obj)

        db.flush()
        question.correct_answer = answers[q.correct_answer_id]

    db.commit()
    db.refresh(quest)
    return quest

def get_quests(db: Session):
    quests = (
        db.query(Quest)
        .join(User, User.id == Quest.creator_id)
        .all()
    )

    res = []
    for quest in quests:
        res.append({
            "id": quest.id,
            "text": quest.text,
            "creator_id": quest.creator_id,
            "creator_name": quest.creator.login
        })

    return res

from fastapi import HTTPException

def get_quest(db: Session, quest_id: int):
    quest = (
        db.query(Quest)
        .join(User, User.id == Quest.creator_id)
        .filter(Quest.id == quest_id)
        .first()
    )

    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")

    return {
        "id": quest.id,
        "text": quest.text,
        "creator_id": quest.creator_id,
        "creator_name": quest.creator.login,
        "questions": quest.questions
    }


def get_question(db: Session, quest_id: int, question_id: int):
    return (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.quest_id == quest_id
        )
        .first()
    )