from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models import Quest, Question, Answer, User
from schemas import QuestCreate
from sqlalchemy.orm import selectinload

async def get_quest(db: AsyncSession, quest_id: int):
    result = await db.execute(
        select(Quest)
        .options(
            selectinload(Quest.creator),
            selectinload(Quest.questions)
            .selectinload(Question.answers),
            selectinload(Quest.questions).selectinload(Question.correct_answer)
        )
        .where(Quest.id == quest_id)
    )
    quest = result.scalar_one_or_none()

    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")

    return quest

async def delete_quest(db: AsyncSession, quest_id, user_id):
    result = await db.execute(
        select(Quest).where(Quest.id == quest_id)
    )
    quest = result.scalar_one_or_none()

    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")

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
        select(Question).where(
            Question.id == question_id,
            Question.quest_id == quest_id
        )
    )
    return result.scalar_one_or_none()
