from sqlalchemy import ForeignKey, String, Column, Integer, DateTime, Boolean, Numeric, Text, JSON
from sqlalchemy.orm import relationship, declarative_base, Session
from db_client import DBClient
from telegram import User

Base = declarative_base()


class DBUser(Base):
    __tablename__: str = 'users'
    user_id_1: Column = Column(String(200), primary_key=True)
    username: Column = Column(String(100), nullable=False)
    first_name: Column = Column(String(200), nullable=True)
    last_name: Column = Column(String(200), nullable=True)
    is_bot: Column = Column(Boolean, nullable=False)
    language_code: Column = Column(String(10), nullable=False)

    user_requests = relationship('user_requests')


class UserRequest(Base):
    __tablename__: str = 'user_requests'
    msg_id: Column = Column(Integer, primary_key=True)
    msg_txt: Column = Column(Text, nullable=False)
    com_type: Column = Column(String(100), nullable=True)
    com_args: Column = Column(JSON, nullable=True)
    msg_time: Column = Column(DateTime, nullable=False)
    user_id_2: Column = Column(String(200), ForeignKey('users.user_id_1'))


def add_new_unique_user(msg_user: User, engine):
    db_user = DBUser(user_id=str(msg_user.id), username=msg_user.username, first_name=msg_user.first_name,
                     last_name=msg_user.last_name, is_bot=msg_user.is_bot, language_code=msg_user.language_code)

    with Session(engine) as db_session:
        query_res = db_session.get(DBUser, str(msg_user.id))
        if query_res is None:
            db_session.add(db_user)
            db_session.commit()
    return None


# if __name__ == '__main__':
#     db_client: DBClient = DBClient()
#     db_engine = db_client.create_sql_alchemy_engine()
#     Base.metadata.drop_all(db_engine)
#     Base.metadata.create_all(db_engine)
