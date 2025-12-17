from datetime import datetime, timezone, timedelta

from sqlalchemy import Column, Integer, String, Boolean, create_engine, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.types import JSON

engine = create_engine("sqlite:///users.db", echo=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    premium_until = Column(DateTime(timezone=True))
    cur_model = Column(String)
    role = Column(String, nullable=True)
    request_cnt = Column(Integer)
    context = Column(MutableList.as_mutable(JSON), default=list, nullable=False)


    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.premium_until = datetime(1970, 1, 1, tzinfo=timezone.utc)
        self.cur_model = "gpt-4o-mini"

    # def __repr__(self):
    #     return "<User('%s', '%s', '%s')>" % (self.telegram_id, self.grade, self.messages_recieving)


# Создание таблицы

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_user(session, telegram_id: int) -> User | None:
    return session.query(User).filter(User.telegram_id == telegram_id).first()


def add_user(telegram_id):
    session = SessionLocal()
    try:
        with session.begin():
            user = get_user(session, telegram_id)
            if user:
                return False
            else:
                session.add(User(telegram_id=telegram_id))
                return True
    finally:
        session.close()

def update_premium(telegram_id):
    session = SessionLocal()
    try:
        with session.begin():
            user = get_user(session, telegram_id)
            if user:
                user.premium_until = datetime.now(timezone.utc) + timedelta(days=30)
                return True
            else:
                return False
    finally:
        session.close()

def update_role(telegram_id, role):
    session = SessionLocal()
    try:
        with session.begin():
            user = get_user(session, telegram_id)
            if user:
                user.role = role
                return True
            else:
                return False
    finally:
        session.close()


def update_model(telegram_id, model):
    session = SessionLocal()
    try:
        with session.begin():
            user = get_user(session, telegram_id)
            if user:
                user.model = model
                return True
            else:
                return False
    finally:
        session.close()

def update_request_cnt(telegram_id):
    session = SessionLocal()
    try:
        with session.begin():
            user = get_user(session, telegram_id)
            if user:
                user.request_cnt += 1
                return True
            else:
                return False
    finally:
        session.close()

def update_context(telegram_id, role, text):
    session = SessionLocal()
    try:
        with session.begin():
            user = get_user(session, telegram_id)
            if user:
                user.context.append({"role": role, "content": text})
                return True
            else:
                return False
    finally:
        session.close()
#
# def delete_account(telegram_id):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     session.query(User).filter_by(telegram_id=telegram_id).delete()
#     session.commit()
#     return
#
# def get_all_tg_ids():
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     data = session.query(User)
#     session.commit()
#     return data

Base.metadata.create_all(engine)