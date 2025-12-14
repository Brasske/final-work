from sqlalchemy.orm import Session
from models import Quest, Question, Answer, User
from schemas import QuestCreate

# def change_quest(db: Session, quest_data: QuestCreate, user):
#     quest = db.query(Quest).filter(Quest.id == quest_data.id)

def delete_quest(db: Session, quest_id, user_id):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()
    
    if not quest:
        raise {"status":"404", "massage": ""}
    if quest.creator_id != user_id:
        raise {"status":"err", "massage": "Пользователь не является владельцем квиза"}
    db.delete(quest)
    db.commit()

    # db.refresh(quest)
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
    quests = db.query(Quest).all()
    res = []
    for quest in quests:
        res.append({
            "id": quest.id,
            "text": quest.text,
            "creator_id": quest.creator_id,
            "creator_name": db.query(User).filter(User.id == quest.creator_id).first().login
        })
    return res


def get_quest(db: Session, quest_id: int):
    quest = db.query(Quest).filter(Quest.id == quest_id).first()
    res = {
            "id": quest.id,
            "text": quest.text,
            "creator_id": quest.creator_id,
            "creator_name": db.query(User).filter(User.id == quest.creator_id).first().login,
            "quests": db.query(Question).filter(Question.quest_id == quest_id).all()
    }
    return res

def get_question(db: Session, quest_id: int, question_id: int):
    question = db.query(Question).filter(Question.id == question_id and Question.quest_id == quest_id).first()
    res = {
        "id": question.id,
        "text": question.text,
        "correct_answer_id": question.correct_answer_id,
        "answers": db.query(Answer).filter(Answer.question_id == question_id).all(),
    }
    
    return res