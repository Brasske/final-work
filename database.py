from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://root:qwerty@localhost:5432/quiz"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def lifespan(fapp: FastAPI):
    # establish a connection to the database    
    fapp.state.async_session = await get_user_db().__anext__()
    yield
    # close the connection to the database
    await fapp.state.async_session.close()
    await fapp.state.async_session.engine.dispose()


async def get_db():
    async with SessionLocal() as db:
        yield db
