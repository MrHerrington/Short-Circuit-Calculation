import json
from config import DB_SECURITY_DIR, ENGINE_ECHO
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


class Base(sa.orm.DeclarativeBase):
    pass


def db_access() -> str:
    with open(DB_SECURITY_DIR, 'r', encoding='UTF-8') as file:
        temp = json.load(file)['db_access']
        login, password, db_name = temp['login'], temp['password'], temp['db_name']
        engine_string = f"mysql+pymysql://{login}:{password}@localhost/{db_name}?charset=utf8mb4"
    return engine_string


engine = sa.create_engine(db_access(), echo=ENGINE_ECHO)
Session = sa.orm.sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as err:
        session.rollback()
        raise err from None
    finally:
        session.close()
