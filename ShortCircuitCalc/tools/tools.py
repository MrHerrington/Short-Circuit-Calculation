# -*- coding: utf-8 -*-
"""This module provides tools for interacting with catalog databases
and utility tools for the main functionality of the program"""


import logging
import json
import re
import typing as ty
from contextlib import contextmanager

import sqlalchemy as sa
import sqlalchemy.orm

from ShortCircuitCalc.config import ROOT_DIR, CONFIG_DIR, CREDENTIALS_DIR, ENGINE_ECHO, SQLITE_DB_NAME


__all__ = ('Base', 'engine', 'metadata', 'session_scope')


logger = logging.getLogger(__name__)


class Base(sa.orm.DeclarativeBase):
    """Child class from DeclarativeBase class sqlalchemy package"""
    pass


def config_manager(param: str, value: ty.Union[str, bool] = False) -> ty.Union[str, bool]:
    """A function that manages configuration parameters.

    Args:
        param (str): The name of the configuration parameter to manage.
        value (str, optional): The new value for the configuration parameter. Defaults to False.

    Returns:
        str or False: The current value of the configuration parameter if value is not provided,
                     or False if the configuration parameter does not exist.

    Raises:
        FileNotFoundError: If the configuration file specified by CONFIG_DIR does not exist.

    This function reads the configuration file specified by CONFIG_DIR, searches for the
    specified configuration parameter, and returns its current value. If a new value is
    provided, the function updates the configuration file with the new value and prints a
    message indicating the change. If the configuration file does not exist, a FileNotFoundError
    is raised.

    Note:
        The configuration file is assumed to be in UTF-8 encoding.

    """
    pattern = re.compile(rf'(?P<name>{param}) = (?P<value>.+)\n')
    config_file = open(CONFIG_DIR, 'r+', encoding='UTF-8')
    current_config_data = config_file.read()
    matched_param = re.search(pattern, current_config_data)

    if not value:
        config_file.close()
        return False if matched_param.group('value') == 'False' else matched_param.group('value').strip("'")

    else:
        value = value if value == 'False' else value.replace(value, f"'{value}'")
        updated_config_data = current_config_data.replace(
            f"{matched_param.group('name')} = {matched_param.group('value')}",
            f"{matched_param.group('name')} = {value}", 1)
        config_file.seek(0)
        config_file.truncate()
        config_file.write(updated_config_data)
        config_file.close()
        logger.warning(f'Config params changed: now {param} = {value}!')


def db_access() -> str:
    """Returns a string representing the database connection URL based on the existing configuration.

    This function checks the existing configuration to determine the type of database connection
    to use. If the configuration specifies a MySQL database, it opens the credentials file, loads
    the necessary data, and constructs the MySQL engine string. If the configuration specifies a
    SQLite database, it returns the SQLite engine string. If the configuration does not specify a
    database connection, it tries to access the MySQL database. If the credentials file is not found,
    it falls back to accessing the SQLite database. If the configuration specifies an unsupported
    database connection type, it resets the configuration parameter and prints an error message.

    Returns:
        str: The database connection URL.

    Note:
        The program prefer MySQL connection so when the method finds the credentials file, it deletes
        the current standalone SQLite database and deploys a new one in the MySQL environment.

    """
    def __mysql_access() -> str:
        """Creates a connection to the MySQL database.

        Service method, opens the credentials file, loads the necessary data,
        and constructs the MySQL engine string.

        Returns:
            the MySQL engine string.

        """
        with open(CREDENTIALS_DIR, 'r', encoding='UTF-8') as file:
            temp = json.load(file)['db_access']
            login, password, db_name = temp['login'], temp['password'], temp['db_name']
            engine_string = f'mysql+pymysql://{login}:{password}@localhost/{db_name}?charset=utf8mb4'

        path_link = ROOT_DIR / SQLITE_DB_NAME
        if path_link.is_file():
            path_link.unlink()
            logger.warning(f"Existing SQLite database '{SQLITE_DB_NAME}' deleted!")

        logger.info('Connected to MySQL database.')

        if config_manager('DB_EXISTING_CONNECTION') != 'MySQL':
            config_manager('DB_EXISTING_CONNECTION', 'MySQL')

        return engine_string

    def __sqlite_access() -> str:
        """Сreates a connection to the SQLite database.

        Service method, returns the SQLite engine string.

        Returns:
            str: The SQLite engine string.

        """
        logger.info('Connected to SQLite database.')

        if config_manager('DB_EXISTING_CONNECTION') != 'SQLite':
            config_manager('DB_EXISTING_CONNECTION', 'SQLite')

        return f'sqlite:///{ROOT_DIR}/{SQLITE_DB_NAME}'

    def __no_db_access() -> str:
        """Chooses a database connection based on the existing configuration.

        A method to handle cases when an existing database connection is not found.
        This function attempts to access the MySQL database and, if unsuccessful,
        falls back to accessing the SQLite database.

        Returns:
            str: The engine string for the accessed database connection.

        """
        logger.warning('Existing connection not found!')

        try:
            logger.info('Accessing MySQL database...')
            logger.info('Credentials initializing...')
            engine_string = __mysql_access()

        except FileNotFoundError:
            logger.warning('Credentials file for MySQL database not found!')
            logger.info('Accessing SQLite database...')
            engine_string = __sqlite_access()

        return engine_string

    connection_types = {
        False: __no_db_access,
        'MySQL': __mysql_access,
        'SQLite': __sqlite_access
    }

    if not hasattr(db_access, 'engine_string'):
        try:
            if CREDENTIALS_DIR.is_file():
                db_access.engine_string = connection_types['MySQL']()
            else:
                db_access.engine_string = connection_types[config_manager('DB_EXISTING_CONNECTION')]()

        except FileNotFoundError:
            config_manager('DB_EXISTING_CONNECTION', 'False')
            logger.warning("The config 'DB_EXISTING_CONNECTION' parameter has been reset. "
                           "Retrying database connection...")
            db_access()

        return db_access.engine_string

    else:
        return db_access.engine_string


engine = sa.create_engine(url=db_access(), echo=ENGINE_ECHO)
metadata = sa.MetaData()
Session = sa.orm.sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(logs: bool = True) -> None:
    """Context manager provides a session for executing database operations.

    Yields:
        session: A session object for executing database operations.
    Args:
        logs (bool, optional): Whether to log errors. Defaults to True.
    Raises:
        Exception: If an error occurs during the execution of the database operations.

    """
    session = Session()
    try:
        yield session
        session.commit()
    except sa.exc.OperationalError as err:
        session.rollback()
        if logs:
            logger.error(err, exc_info=True)
        raise err
    finally:
        session.close()
