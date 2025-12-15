from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CompliteQuestion(Base):
    __tablename__ = 'complite_questions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='complite_questions')

    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    question = relationship('Question', back_populates='users_complite')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String)    

    created_quiz = relationship('Quest', back_populates='creator')

    complite_questions = relationship('CompliteQuestion', back_populates='user')


class Quest(Base):
    __tablename__ = 'quests'
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)

    questions = relationship('Question', back_populates='quest', cascade='all, delete')

    creator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    creator = relationship('User', back_populates='created_quiz')

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)

    answers = relationship(
        'Answer',
        cascade='all, delete',
        back_populates='question',
        foreign_keys='Answer.question_id'
    )

    correct_answer_id = Column(Integer, ForeignKey('answers.id', ondelete='SET NULL'), nullable=True)

    correct_answer = relationship(
        'Answer',
        foreign_keys=[correct_answer_id],
        post_update=True
    )

    quest_id = Column(Integer, ForeignKey('quests.id', ondelete='CASCADE'), nullable=False)
    quest = relationship('Quest', back_populates='questions')

    users_complite = relationship('CompliteQuestion', back_populates='question')

class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)

    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)

    question = relationship(
        'Question',
        back_populates='answers',
        foreign_keys=[question_id]
    )
