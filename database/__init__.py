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

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """The method automatically generates a table name.

        The method automatically generates a table name based
        on the snake_case-style ORM model.

        Returns:
            str: The name of the table in the snake_case style.

        """
        return BaseMixin.__camel_to_snake(cls.__name__)

    @declared_attr
    @classmethod
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
        Filtrate query sample:
            PowerNominal.read_table(filtrate='power <= 63') or
            VoltageNominal.read_table(filtrate="voltage = Decimal('0.4')")
        Returns:
            pd.DataFrame: Object with query results

        """
        # noinspection PyArgumentList
        with session_scope() as session:
            if filtrate is None:
                df = pd.read_sql(session.query(cls).statement, session.bind)[:limit]
            else:
                df = pd.read_sql(session.query(cls).filter(sa.text(filtrate)).statement, session.bind)[:limit]
        return df

    @classmethod
    def show_table(cls, filtrate: ty.Optional[str] = None, limit: ty.Optional[int] = None,
                   indexes: bool = False) -> None:
        """The method shows the table.

        Args:
            filtrate (Optional[str]): Defaults to None. Accepts the filtering condition.
            limit (Optional[int]): Defaults shows all results, otherwise shows the specified number of results.
            indexes (bool): Parameter shows rows indexes of the query results.
        Filtrate query sample:
            PowerNominal.show_table(filtrate='power <= 63') or
            VoltageNominal.show_table(filtrate='voltage = 0.4')
        Note:
             This method prints query statement.

        """
        df = cls.read_table(filtrate=filtrate, limit=limit)
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=indexes))

    @classmethod
    def insert_table(cls, data: ty.List[dict]) -> None:
        """The method inserts values in chosen table.

        This method allows to add records to the table
        both as individual values and as bulk operations.

        Args:
            data (List[dict]): A list with dictionary(es) of values.

        Sample:
            PowerNominals.insert_table({'id': 1, 'power': 25}, {'id':9, 'power': 1000})

        """
        # noinspection PyArgumentList
        with session_scope() as session:
            result = session.connection().execute(sa.insert(cls), data).rowcount
            print(f"Table '{cls.__tablename__}' has been updated. {result} string(s) were inserted.")

    @classmethod
    def update_table(cls, data: ty.Union[ty.List[dict], dict], options: ty.Optional[str] = 'primary_keys',
                     attr: str = None, alias: str = None, criteria: ty.Iterable = None) -> None:
        """The method updates values in chosen table.

        This method allows to update records to the table both as individual values and as bulk operations.

        Args:
            data (Union[List[dict], dict]): A list with dictionary(es) of values or dict with one string.
            options (Optional[str]): Defaults by 'primary_keys', also available 'with_alias' and 'where condition'.
            attr (str): Defaults by None, name attribute in filter for 'with_alias' or 'where condition' method.
            alias (str): Defaults by None, name alias for 'with_alias' method.
            criteria (Iterable): Defaults by None, iterable object with values to filtering update query
            in 'where condition' method.

        Samples:
            for 'primary_keys' method:
                PowerNominals.update_table({'id': 1, 'power': 25}, {'id':9, 'power': 1000})
            for 'with_alias' method:
                Transformer.update_table({'vol_id': 2, 'power_id': 10}, options='with_alias',
                                            attr='voltage_id', alias='vol_id')
            for 'where_conditions' method:
                Transformer.update_table({'power': 630}, options='where_condition', attr='power', criteria=[250, 400])

        """
        def __primary_keys():
            # noinspection PyArgumentList
            with session_scope() as session:
                return session.execute(sa.update(cls), data).rowcount

        def __with_alias():
            # noinspection PyArgumentList
            with session_scope() as session:
                return session.connection().execute(
                    sa.update(cls).where(getattr(cls, attr) == sa.bindparam(alias)), data).returned_defaults

        def __where_condition():
            # noinspection PyArgumentList
            with session_scope() as session:
                return session.execute(sa.update(cls).where(getattr(cls, attr).in_(criteria)).values(data)).rowcount

        methods = {
            'primary_keys': __primary_keys,
            'with_alias': __with_alias,
            'where_condition': __where_condition
        }

        print(f"Table '{cls.__tablename__}' has been updated. {methods[options]()} matches found!")

    @classmethod
    def delete_table(cls, filtrate: ty.Optional[str] = None) -> None:
        """The method inserts values in chosen table.

        Args:
            filtrate (Optional[str]): Defaults to None. Accepts the filtering condition.

        Sample:
            Transformer.delete_table('id > 20')

        """
        # noinspection PyArgumentList
        with session_scope() as session:
            rows_deleted = session.connection().execute(sa.delete(cls).filter(sa.text(filtrate))).rowcount
            print(f"Rows were deleted from table '{cls.__tablename__}'. {rows_deleted} matches found!")

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
