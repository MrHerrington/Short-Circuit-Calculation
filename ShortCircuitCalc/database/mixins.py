# -*- coding: utf-8 -*-
"""The module presents class BaseMixin, which extends
the functionality of the declarative base class 'Base'"""


import typing as ty
import pathlib
import re
import csv
import sqlalchemy as sa
from sqlalchemy.orm import declared_attr
import sqlalchemy.exc
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from ..tools import Base, engine, session_scope


__all__ = ('BaseMixin',)


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
        return cls.__camel_to_snake(cls.__name__)

    @declared_attr
    @classmethod
    def id(cls) -> sa.orm.Mapped[sa.Integer]:
        """The method generates primary keys.

        The method automatically generates primary keys with auto increment.

        Returns:
            The return a column of the primary keys."""

        return sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True, sort_order=0)

    @classmethod
    def create_table(cls, drop_first: bool = False, forced_drop: bool = False) -> None:
        """The method creates the table.

        The method create table. If successful, outputs the info message.

        Args:
            drop_first (bool): defaults by False, drop table first if existing.
            forced_drop (bool): Force drop table bypassing foreign key constraint.

        """
        if drop_first and forced_drop:
            cls.drop_table(cls.__tablename__, forced=True)
        elif drop_first:
            cls.drop_table(cls.__tablename__)
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
        with session_scope() as session:
            if filtrate is None:
                df = pd.read_sql(session.query(cls).statement, session.bind, dtype=object)[:limit]
            else:
                df = pd.read_sql(
                    session.query(cls).filter(sa.text(filtrate)).statement, session.bind, dtype=object)[:limit]
        return df

    @classmethod
    def show_table(cls, gui: bool = False, filtrate: ty.Optional[str] = None, limit: ty.Optional[int] = None,
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
        if not gui:
            print(tabulate(df, headers='keys', tablefmt='psql', numalign='center', showindex=indexes))
        else:
            fig, ax = plt.subplots()
            ax.axis('tight')
            ax.axis('off')
            table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
            table.auto_set_column_width(col=list(range(len(df.columns))))
            # table.set_fontsize(12)
            # table.scale(1, 1)
            plt.get_current_fig_manager().window.state('zoomed')
            plt.show()

    @classmethod
    def insert_table(cls, data: ty.Optional[ty.List[dict]] = None,
                     from_csv: ty.Union[str, pathlib.WindowsPath] = None) -> None:
        """The method inserts values in chosen table.

        This method allows to add records to the table
        both as individual values and as bulk operations.
        Also, available from CSV format values insert.

        Args:
            data (List[dict]): A list with dictionary(es) of values. Defaults by None, if from_csv param is True.
            from_csv (Union[str, pathlib.WindowsPath]): Path to the CSV-file.

        Sample:
            PowerNominals.insert_table({'id': 1, 'power': 25}, {'id':9, 'power': 1000}) or
            PowerNominals.insert_table(DATA_DIR/'power')

        """
        if all((data is None, from_csv is None)):
            raise ValueError('Requires at least one not NoneType argument!')
        if from_csv:
            data = BaseMixin.__csv_to_list_of_dicts(from_csv)
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
            with session_scope() as session:
                return session.execute(sa.update(cls), data).rowcount

        def __with_alias():
            with session_scope() as session:
                return session.connection().execute(
                    sa.update(cls).where(getattr(cls, attr) == sa.bindparam(alias)), data).returned_defaults

        def __where_condition():
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
        with session_scope() as session:
            rows_deleted = session.connection().execute(sa.delete(cls).filter(sa.text(filtrate))).rowcount
            print(f"Rows were deleted from table '{cls.__tablename__}'. {rows_deleted} matches found!")

    @classmethod
    def drop_table(cls, confirm: ty.Union[ty.Callable, str, None] = None, forced: bool = False) -> None:
        """The method drops the table.

        Args:
            confirm (Union[Callable, str], optional): Accepts confirmation of table deletion.
            forced (bool): Force drop table bypassing foreign key constraint.
        Note:
             To drop table, enter the name of the table in the form of 'cls.__tablename__'
             or in the format of a string.

        """
        try:
            if confirm == cls.__tablename__:
                if not forced:
                    Base.metadata.tables[cls.__tablename__].drop(engine)
                    print(f"Table '{cls.__tablename__}' has been deleted.")
                else:

                    # MySQL dialect
                    try:
                        with session_scope() as session:
                            session.execute(sa.text(f'SET FOREIGN_KEY_CHECKS = 0;'))
                            session.execute(sa.text(f'DROP TABLE {cls.__tablename__};'))
                            session.execute(sa.text(f'SET FOREIGN_KEY_CHECKS = 1'))

                    # SQLite dialect
                    except sa.exc.OperationalError:
                        with session_scope() as session:
                            session.execute(sa.text(f'PRAGMA FOREIGN_KEYS = OFF;'))
                            session.execute(sa.text(f'DROP TABLE {cls.__tablename__};'))
                            session.execute(sa.text(f'PRAGMA FOREIGN_KEYS = ON'))

                    print(f"Table '{cls.__tablename__}' has been forced deleted.")
            else:
                raise f"Table '{cls.__tablename__}' deletion not confirmed."
        except sa.exc.OperationalError as err:
            if 'Unknown table' in err.orig.__str__() or 'no such table' in err.orig.__str__():
                print(f"There is no need to delete the table '{cls.__tablename__}', it does not exist")
            else:
                raise err from None

    @classmethod
    def reset_id(cls) -> None:
        """The method reset id order for the table with updating in child tables."""

        # MySQL dialect
        try:
            with session_scope() as session:
                session.execute(sa.text(f'SET @count = 0;'))
                session.execute(
                    sa.text(f'UPDATE {cls.__tablename__} SET {cls.__tablename__}.id = @count:= @count + 1;'))
                session.execute(sa.text(f'ALTER TABLE {cls.__tablename__} AUTO_INCREMENT = 1'))
            print(f"id order for table '{cls.__tablename__}' has been reset!")

        # SQLite dialect
        except sa.exc.OperationalError:
            print('For SQLite basically without AUTOINCREMENT rowid is '
                  'determined according to the highes existing rowid, '
                  'so if none exist then the rowid will be 1')

    _new_name: ty.ClassVar[ty.Optional[str]]

    @classmethod
    def __camel_to_snake(cls, name: str) -> str:

        """The method converts the register.

        A utility method that converts the name of the ORM model of
        the table from the UpperCamelCase register to snake_case.

        Args:
            name (str): Default table name.
        Returns:
            str: Return new table name.

        """
        if not hasattr(cls, '_new_name'):
            name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
            cls._new_name = name
        return cls._new_name

    @classmethod
    def __csv_to_list_of_dicts(cls, path: ty.Union[str, pathlib.WindowsPath]) -> ty.List[dict]:
        """The method converts CSV-file datas into list of the dictionaries.

        Args:
            path: Union[str, pathlib.WindowsPath]: Path to the CSV-file.
        Returns:
            List[dict]: CSV-file datas into list of the dictionaries.

        """
        with open(path, 'r', encoding='UTF-8') as tmp_file:
            tmp_data = map(lambda x: {k: cls.__convert_types(v) for k, v in x.items()}, csv.DictReader(tmp_file))
            return list(tmp_data)

    @staticmethod
    def __convert_types(val) -> ty.Union[int, float, str]:
        """The method converts val type.

        Args:
            val (str): Value in string format from CSV file
        Returns:
            Union[int, float, str]: Value with new type.

        """
        val_types = (int, float)
        for type_ in val_types:
            try:
                val = type_(val)
                return val
            except ValueError:
                continue
        return val
