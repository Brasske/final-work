from fastapi import FastAPI
from database import engine, Base
from routers import auth, quests, user

app = FastAPI()

app.include_router(auth.router)
app.include_router(quests.router)
app.include_router(user.router)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
