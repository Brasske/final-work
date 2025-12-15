from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models import Quest, Question, Answer, User, CompliteQuestion
from schemas import QuestCreate
from sqlalchemy.orm import selectinload, load_only

async def get_quest(db: AsyncSession, quest_id: int):
    result = await db.execute(
        select(Quest)
        .options(
            selectinload(Quest.creator).load_only(User.username, User.id),
            selectinload(Quest.questions)
            .selectinload(Question.answers),
            selectinload(Quest.questions).selectinload(Question.correct_answer)
        )
        .where(Quest.id == quest_id)
    )
    quest = result.scalar_one_or_none()

    if not quest:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    return quest

async def delete_quest(db: AsyncSession, quest_id, user_id):
    result = await db.execute(
        select(Quest).where(Quest.id == quest_id)
    )
    quest = result.scalar_one_or_none()

    if not quest:
        raise HTTPException(status_code=404, detail="Квиз не найден")

    if quest.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Пользователь не владелец квиза")

    await db.delete(quest)
    await db.commit()

    return {"status": "ok"}

async def create_quest(db: AsyncSession, quest_data: QuestCreate, user):
    quest = Quest(
        text=quest_data.text,
        creator_id=user.id
    )

    db.add(quest)
    await db.flush()

    for q in quest_data.questions:
        question = Question(text=q.text, quest=quest)
        db.add(question)
        await db.flush()

        answers = []
        for a in q.answers:
            obj = Answer(text=a.text, question=question)
            db.add(obj)
            answers.append(obj)

        await db.flush()
        question.correct_answer = answers[q.correct_answer_id]

    await db.commit()
    await db.refresh(quest)
    return quest



async def get_question(db: AsyncSession, quest_id: int, question_id: int):
    result = await db.execute(
        select(Question).options(
            selectinload(Question.answers),
        ).where(
            Question.id == question_id,
            Question.quest_id == quest_id
        )
    )
    return result.scalar_one_or_none()

async def get_answer(question_id: int,user_id: int, db: AsyncSession):
    q = await db.execute(
        select(CompliteQuestion)
        .where(
            CompliteQuestion.question_id == question_id,
            CompliteQuestion.user_id == user_id
            ))
    
    if not q:
        com_question = CompliteQuestion(user_id=user_id, question_id=question_id)
        db.add(com_question)
        await db.commit()
        await db.refresh(com_question)
    