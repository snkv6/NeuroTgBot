from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.types import JSON

engine = create_engine("sqlite:///users.db", echo=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    is_premium = Column(Boolean)
    cur_model = Column(String)
    request_cnt = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    context = Column(MutableList.as_mutable(JSON), default=list, nullable=False)


    def __init__(self, _telegram_id):
        self.telegram_id = _telegram_id
        self.is_premium = False
        self.cur_model = "gpt-4o-mini"

    # def __repr__(self):
    #     return "<User('%s', '%s', '%s')>" % (self.telegram_id, self.grade, self.messages_recieving)


# Создание таблицы


# def check_user_existence(telegram_id):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     data = (session.query(User).filter(User.telegram_id == telegram_id).first() == None)
#     session.commit()
#     return data
#
#
def add_user(telegram_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        with session.begin():
            exists = session.query(User.id).filter(User.telegram_id == telegram_id).first()
            if not exists:
                session.add(User(telegram_id))
                session.commit()
    finally:
        session.close()
#
# def change_users_grade(telegram_id, grade):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     session.query(User).filter(User.telegram_id == telegram_id).first().grade = grade
#     session.commit()
#     return
#
# def change_messages_recieving(telegram_id):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     session.query(User).filter(User.telegram_id == telegram_id).first().messages_recieving = not session.query(User).filter(User.telegram_id == telegram_id).first().messages_recieving
#     session.commit()
#     return
#
# def get_grade(telegram_id):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     data = session.query(User).filter(User.telegram_id == telegram_id).first().grade
#     session.commit()
#     return data
#
# def get_messages_recieving(telegram_id):
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     data = session.query(User).filter(User.telegram_id == telegram_id).first().messages_recieving
#     session.commit()
#     return data
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