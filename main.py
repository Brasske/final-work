from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from database import engine, Base, get_db
from routers import auth, quests, user

import asyncio




app = FastAPI()

app.include_router(auth.router)
app.include_router(quests.router)
app.include_router(user.router)


@app.on_event("startup")
async def on_startup():
    # создаём все таблицы через async engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
