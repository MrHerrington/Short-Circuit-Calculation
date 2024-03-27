import json
from config import DB_SECURITY_DIR
import sqlalchemy as sa
import sqlalchemy.orm


class Base(sa.orm.DeclarativeBase):
    pass


def db_access() -> str:
    with open(DB_SECURITY_DIR, 'r', encoding='UTF-8') as file:
        temp = json.load(file)['db_access']
        login, password, db_name = temp['login'], temp['password'], temp['db_name']
        engine_string = f"mysql+pymysql://{login}:{password}@localhost/{db_name}?charset=utf8mb4"
    return engine_string


engine = sa.create_engine(db_access(), echo=True)
Session = sa.orm.sessionmaker(bind=engine)

