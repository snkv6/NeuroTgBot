import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# DB_PATH = Path(__file__).resolve().parent / "database.db"
# DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

load_dotenv("keys/.env")
DATABASE_URL = os.getenv("DATABASE_URL_R")
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def init_db() -> None:
    import database.users
    import database.payments

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
