# -*- coding: utf-8 -*-
"""This module provides tools for interacting with catalog databases
and utility tools for the main functionality of the program"""


import json
from pathlib import Path
from contextlib import contextmanager
import sqlalchemy as sa
import sqlalchemy.orm
from ShortCircuitCalc.config import CREDENTIALS_DIR, ENGINE_ECHO, SQLITE_DB_NAME


class Base(sa.orm.DeclarativeBase):
    """Child class from DeclarativeBase class sqlalchemy package"""
    pass


def db_access() -> str:
    """This function responsible for accessing the database.

    Returns:
        Return engine string with access info from security JSON file.

    """
    if not hasattr(db_access, 'engine_string'):
        try:
            print('Accessing MySQL database...')
            print('Credentials initializing...')
            with open(CREDENTIALS_DIR, 'r', encoding='UTF-8') as file:
                temp = json.load(file)['db_access']
                login, password, db_name = temp['login'], temp['password'], temp['db_name']
                db_access.engine_string = f"mysql+pymysql://{login}:{password}@localhost/{db_name}?charset=utf8mb4"
            print('Credentials initialized!')
            path_link = Path(SQLITE_DB_NAME)
            if path_link.is_file():
                path_link.unlink()
                print(f"Existing SQLite database '{SQLITE_DB_NAME}' deleted!")
        except FileNotFoundError:
            print('Credentials file for MySQL database not found!')
            print('Accessing SQLite database...')
            db_access.engine_string = f"sqlite:///{SQLITE_DB_NAME}"
    if 'mysql' in db_access.engine_string:
        print('MySQL database connected!')
    elif 'sqlite' in db_access.engine_string:
        print('SQLite database connected!')
    return db_access.engine_string


engine = sa.create_engine(url=db_access(), echo=ENGINE_ECHO)
metadata = sa.MetaData()
Session = sa.orm.sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope() -> None:
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
