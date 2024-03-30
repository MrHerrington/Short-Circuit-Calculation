# -*- coding: utf-8 -*-
"""This package implements the 'BaseMixin' class, which is necessary to
extend the functionality of the declarative base class 'Base', including:
- automatic generation of table names based on ORM models in the snake_case style;
- automatic generation of primary keys with auto increment.
- the basic implementation of the CRUD interface for working
with the selected database table is presented.

The package also presents ORM models of the database of various electrical devices."""


import sqlalchemy as sa
from sqlalchemy.orm import declared_attr
import sqlalchemy.exc
from tools import Base, engine, session_scope
import typing as ty
import re
import pandas as pd
from tabulate import tabulate


class BaseMixin:
    """Class extends the functionality of the declarative base class 'Base'"""
    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """The method automatically generates a table name.

        The method automatically generates a table name based
        on the snake_case-style ORM model.

        Returns:
            str: The name of the table in the snake_case style.

        """
        return BaseMixin.__camel_to_snake(cls.__name__)

    @classmethod
    @declared_attr
    def id(cls) -> sa.orm.Mapped[sa.Integer]:
        """The method generates primary keys.

        The method automatically generates primary keys with auto increment.

        Returns:
            The return a column of the primary keys."""

        return sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True, sort_order=0)

    @classmethod
    def create_table(cls) -> None:
        """The method creates the table.

        The method create table. If successful, outputs the message
        'Table <tablename> has been created.', outputs
        'Table <tablename> already exists.' otherwise.

        """
        try:
            Base.metadata.tables[cls.__tablename__].create(engine)
            print(f"Table '{cls.__tablename__}' has been created.")
        except sa.exc.OperationalError as err:
            print(f"{type(err)}: Table '{cls.__tablename__}' already exists!")

    @classmethod
    def read_table(cls, filtrate: ty.Optional[str] = None, limit: ty.Optional[int] = None) -> pd.DataFrame:
        """The method reads the table.

        Args:
            filtrate (Optional[str]): Defaults to None. Accepts the filtering condition.
            limit (Optional[int]): Default shows all results, otherwise shows the specified number of results.
        Returns:
            pd.DataFrame: Object with query results

        """
        # noinspection PyArgumentList
        with session_scope() as session:
            if filtrate is None:
                df = pd.read_sql(session.query(cls).statement, session.bind)[:limit]
            else:
                df = pd.read_sql(session.query(cls).filter(
                                                            eval(cls.__filtration_alchemy(filtrate))
                                                            ).statement, session.bind)[:limit]
        return df

    @classmethod
    def show_table(cls, filtrate: ty.Optional[str] = None, limit: ty.Optional[int] = None,
                   indexes: bool = False) -> None:
        """The method shows the table.

        Args:
            filtrate (Optional[str]): Defaults to None. Accepts the filtering condition.
            limit (Optional[int]): Defaults shows all results, otherwise shows the specified number of results.
            indexes (bool): Parameter shows rows indexes of the query results.
        Note:
             This method prints query statement.

        """
        df = cls.read_table(filtrate=filtrate, limit=limit)
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=indexes))

    @classmethod
    def insert_table(cls, data: ty.List[dict]) -> None:
        """The method inserts values in chosen table.

        This method allows you to add records to the table
        both as individual values and as batch records.

        Args:
            data (List[dict]): A list with dictionary(es) of values.

        """
        # noinspection PyArgumentList
        with session_scope() as session:
            session.execute(sa.insert(cls), data)
            print(f"Table '{cls.__tablename__}' has been updated. {len(data)} record(s) were inserted")

    # @classmethod
    # def update_table(cls, data: ty.List[dict]) -> None:
    #     # noinspection PyArgumentList
    #     with session_scope() as session:
    #         session.execute(sa.insert(cls), data)
    #         print(f"Table '{cls.__tablename__}' has been updated. {len(data)} record(s) were inserted")

    @classmethod
    def drop_table(cls, confirm: ty.Union[ty.Callable, str, None] = None) -> None:
        """The method drops the table.

        Args:
            confirm (Union[Callable, str], optional): Accepts confirmation of table deletion.
        Note:
             To drop table, enter the name of the table in the form of 'cls.__tablename__'
             or in the format of a string.

        """
        try:
            if confirm == cls.__tablename__:
                Base.metadata.tables[cls.__tablename__].drop(engine)
                print(f"Table '{cls.__tablename__}' has been deleted.")
            else:
                raise f"Table '{cls.__tablename__}' deletion not confirmed."
        except sa.exc.OperationalError as err:
            raise err from None

    @classmethod
    def __filtration_alchemy(cls, expression: str) -> str:
        """The method converts filter expression.

        A utility method that converts the filter expression
        into new format expression for success query.

        Args:
            expression (str): Default expression.
        Returns:
            str: Return new format expression.

        """
        for attr in cls.__getattribute__(cls, '__table__').columns.keys():
            expression = re.sub(attr, 'cls.%s' % attr, expression)
        return expression

    @staticmethod
    def __camel_to_snake(name: str) -> str:
        """The method converts the register.

        A utility method that converts the name of the ORM model of
        the table from the UpperCamelCase register to snake_case.

        Args:
            name (str): Default table name.
        Returns:
            str: Return new table name

        """
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
