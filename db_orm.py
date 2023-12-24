from sqlalchemy import ForeignKey, String, Column, Integer, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.orm import relationship, declarative_base, Session
from telegram import User, Update
from datetime import datetime
from base_log import LoggerHand
from dictionary_model import WordDef
from db_client import DBClient

log = LoggerHand(__name__, f"loggers/{__name__}.log")

Base = declarative_base()


class DBUser(Base):
    __tablename__: str = 'users'
    user_id: Column = Column(String(200), primary_key=True)
    username: Column = Column(String(100), nullable=False)
    first_name: Column = Column(String(200), nullable=True)
    last_name: Column = Column(String(200), nullable=True)
    is_bot: Column = Column(Boolean, nullable=False)
    language_code: Column = Column(String(10), nullable=False)

    user_requests = relationship('UserRequest')

    def __str__(self):
        return f"username: {self.username}, user_id: {self.user_id}"


class UserRequest(Base):
    __tablename__: str = 'user_requests'
    msg_id: Column = Column(Integer, primary_key=True)
    msg_txt: Column = Column(Text, nullable=False)
    com_type: Column = Column(String(100), nullable=True)
    com_args: Column = Column(JSON, nullable=True)
    msg_time: Column = Column(DateTime, nullable=False)
    user_id: Column = Column(String(200), ForeignKey('users.user_id'))

    en_word_dict = relationship('DBDictionary')

    def __str__(self):
        return f"msg: {self.msg_txt} from user: {self.user_id}"


def add_new_unique_user(msg_user: User, engine):
    db_user = DBUser(user_id=str(msg_user.id), username=msg_user.username, first_name=msg_user.first_name,
                     last_name=msg_user.last_name, is_bot=msg_user.is_bot, language_code=msg_user.language_code)

    with Session(engine) as db_session:
        query_res = db_session.get(DBUser, str(msg_user.id))
        if query_res is None:
            db_session.add(db_user)
            db_session.commit()
            log.logger.debug(f"New user has been inserted into the users: {db_user}")
    return None


def add_users_request(msg: Update, engine, func_args: dict):
    db_user_request = UserRequest(msg_txt=msg.message.text, com_type=func_args.get('com_type'),
                                  com_args=func_args, msg_time=datetime.now(),
                                  user_id=msg.message.from_user.id)
    with Session(engine) as db_session:
        db_session.add(db_user_request)
        db_session.commit()
        log.logger.debug(f"New user msg has been inserted into the users_requests: {db_user_request}")
    return db_user_request


class DBDictionary(Base):
    __tablename__ = 'en_word_dict'
    row_id: Column = Column(Integer, primary_key=True)
    user_word: Column = Column(String(100), nullable=False)
    audio_http: Column = Column(String(200), nullable=True)
    part_of_speech: Column = Column(String(50), nullable=True)
    definition: Column = Column(String(700), nullable=True)
    example: Column = Column(String(700), nullable=True)
    user_msg_id: Column = Column(Integer, ForeignKey('user_requests.msg_id'))

    def __str__(self):
        return f"id: {self.row_id}, word: {self.user_word}, definition: {self.definition}"


def add_new_en_word(db_user_request: UserRequest, engine, word_def: WordDef):
    en_word_def = DBDictionary(user_word=word_def.user_word, audio_http=word_def.audio_http,
                               part_of_speech=word_def.part_of_speech, definition=word_def.definition,
                               example=word_def.example, user_msg_id=db_user_request.msg_id)
    with Session(engine) as db_session:
        db_session.add(en_word_def)
        db_session.commit()
        log.logger.debug(f"New definition has been written into DB: {en_word_def}")
    return None


class DBWeather(Base):
    __tablename__ = 'weather_info'
    row_id: Column = Column(Integer, primary_key=True)
    w_date: Column = Column(DateTime, nullable=False)
    city: Column = Column(String(50), nullable=True)
    region: Column = Column(String(50), nullable=True)
    country: Column = Column(String(50), nullable=True)
    condition: Column = Column(String(40), nullable=True)
    avg_temp: Column = Column(Float, nullable=True)
    min_temp: Column = Column(Float, nullable=True)
    max_temp: Column = Column(Float, nullable=True)
    wind_vel: Column = Column(Float, nullable=True)
    user_msg_id: Column = Column(Integer, ForeignKey('user_requests.msg_id'))
    
    def __str__(self):
        return f"The new weather state has been written into DB: " \
               f"{self.row_id}, {self.w_date}, {self.city}, {self.avg_temp}"
#
# if __name__ == '__main__':
#     db_client: DBClient = DBClient()
#     db_engine = db_client.create_sql_alchemy_engine()
#     Base.metadata.drop_all(db_engine)
#     Base.metadata.create_all(db_engine)
