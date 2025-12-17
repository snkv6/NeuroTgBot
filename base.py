from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import Column, Integer, String, Boolean, create_engine, DateTime, select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import JSON

engine = create_async_engine("sqlite+aiosqlite:///users.db", echo=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    premium_until = Column(DateTime)
    cur_model = Column(String)
    role = Column(String, nullable=True)
    request_cnt = Column(Integer, nullable=False, default=0)
    context = Column(MutableList.as_mutable(JSON), default=list, nullable=False)


    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.premium_until = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.cur_model = "gpt-4o-mini"
        self.role = None
        self.request_cnt = 0
        self.context = []

    # def __repr__(self):
    #     return "<User('%s', '%s', '%s')>" % (self.telegram_id, self.grade, self.messages_recieving)


# Создание таблицы

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_user(session, telegram_id: int) -> User | None:
    query = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return query.scalar_one_or_none()

async def add_user(telegram_id):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                return False
            else:
                session.add(User(telegram_id=telegram_id))
                return True


async def update_premium(telegram_id):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                cur_time = datetime.utcnow()
                if user.premium_until < cur_time:
                    user.premium_until = cur_time + timedelta(days=30)
                else:
                    user.premium_until += timedelta(days=30)
                return True
            else:
                return False


async def update_role(telegram_id, role):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                user.role = role
                return True
            else:
                return False



async def update_model(telegram_id, model):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                user.cur_model = model
                return True
            else:
                return False


async def update_request_cnt(telegram_id):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                user.request_cnt += 1
                return True
            else:
                return False


async def update_context(telegram_id, role, text):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                user.context.append({"role": role, "content": text})
                return True
            else:
                return False


async def delete_context(telegram_id):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                user.context.clear()
                return True
            else:
                return False

async def check_premium(telegram_id):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                return user.premium_until < datetime.utcnow()
            else:
                return False

async def get_remaining_premium_days(telegram_id):
    async with SessionLocal() as session:
        async with session.begin():
            user = await get_user(session, telegram_id)
            if user:
                remaining = (user.premium_until - datetime.utcnow()).days
                if remaining < 0:
                    remaining = 0
                return remaining
            else:
                return 0

#
# def get_all_tg_ids():
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     data = session.query(User)
#     session.commit()
#     return data

# Base.metadata.create_all(engine)

# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
