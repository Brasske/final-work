from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models import Quest, Question, Answer, User, UserCompletedQuestion
from schemas import QuestCreate
from sqlalchemy import delete, select, exists, func
from sqlalchemy.orm import selectinload, load_only, joinedload

async def get_quests(db: AsyncSession):
    result = await db.execute(
        select(Quest)
        .options(
            selectinload(Quest.creator).load_only(User.id),
            selectinload(Quest.creator).load_only(User.login),
        )
    )
    quests = result.scalars().all()
    return quests

async def get_my_quests(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Quest).where(Quest.creator_id == user_id)
    )
    quests = result.scalars().all()
    return quests

async def get_quest(db: AsyncSession, quest_id: int):
    result = await db.execute(
        select(Quest)
        .options(
            selectinload(Quest.creator).load_only(User.username, User.id),
            selectinload(Quest.questions).load_only(Question.id, Question.text, Question.quest_id)
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


async def update_quest(
    db: AsyncSession,
    quest_id: int,
    quest_update_data: QuestCreate,  
    user_id: int  
):
    result = await db.execute(
        select(Quest)
        .options(
            selectinload(Quest.questions)
            .selectinload(Question.answers),
            selectinload(Quest.questions)
            .selectinload(Question.correct_answer)
        )
        .where(Quest.id == quest_id, Quest.creator_id == user_id)
    )
    quest = result.scalar_one_or_none()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Квиз не найден или доступ запрещён")

    quest.text = quest_update_data.text

    for old_question in quest.questions:
        await db.execute(
            delete(Answer).where(Answer.question_id == old_question.id)
        )
        await db.delete(old_question)

    quest.questions = []

    for q_data in quest_update_data.questions:
        new_question = Question(text=q_data.text, quest=quest)
        db.add(new_question)
        await db.flush() 

        answers = []
        for a_data in q_data.answers:
            answer = Answer(text=a_data.text, question=new_question)
            db.add(answer)
            answers.append(answer)

        await db.flush()
        new_question.correct_answer = answers[q_data.correct_answer_id]

    await db.commit()
    await db.refresh(quest)
    return quest



async def get_question(db: AsyncSession, quest_id: int, question_id: int):
    result = await db.execute(
        select(Question).options(
            load_only(Question.text),
            selectinload(Question.answers),
        ).where(
            Question.id == question_id,
            Question.quest_id == quest_id
        )
    )
    return result.scalar_one_or_none()

async def get_question_with_correct_answer(db: AsyncSession, quest_id: int, question_id: int):
    result = await db.execute(
        select(Question).options(
            selectinload(Question.answers),
        ).where(
            Question.id == question_id,
            Question.quest_id == quest_id
        )
    )
    return result.scalar_one_or_none()


async def record_correct_answer(
    db: AsyncSession,
    user_id: int,
    quest_id: int,
    question_id: int
) -> bool:
    exists_query = await db.execute(
        select(exists().where(
            UserCompletedQuestion.user_id == user_id,
            UserCompletedQuestion.question_id == question_id
        ))
    )
    if exists_query.scalar():
        return False  

    record = UserCompletedQuestion(
        user_id=user_id,
        question_id=question_id,
        quest_id=quest_id  
    )
    db.add(record)
    await db.commit()
    return True
    

async def get_user_quest_progress(db: AsyncSession, user_id: int):
    subq = (
        select(
            UserCompletedQuestion.quest_id,
            func.count(UserCompletedQuestion.id).label("completed_count")
        )
        .where(UserCompletedQuestion.user_id == user_id)
        .group_by(UserCompletedQuestion.quest_id)
        .subquery()
    )

    result = await db.execute(
        select(Quest, subq.c.completed_count)
        .join(subq, Quest.id == subq.c.quest_id)
        .options(joinedload(Quest.creator)) 
        .order_by(Quest.id)
    )

    return result.all() 