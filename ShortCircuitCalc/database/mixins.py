# -*- coding: utf-8 -*-
"""
The module presents mixin classes, which extends
the functionality of the declarative base class 'Base'.

"""


import logging
import pathlib
import re
import csv
import typing as ty

import sqlalchemy as sa
import sqlalchemy.exc
from sqlalchemy.orm import declared_attr
from sqlalchemy.inspection import inspect
import pandas as pd
from matplotlib import figure

from ShortCircuitCalc.tools import *


__all__ = ('BaseMixin', 'JoinedMixin')


logger = logging.getLogger(__name__)


BT = ty.TypeVar('BT', bound=Base)


class BaseMixin:
    """Class extends the functionality of the declarative base class 'Base'"""

    __new_name: str = None

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
            Base.metadata.tables[cls.__tablename__].create(engine, checkfirst=True)
            logger.warning(f"Table '{cls.__tablename__}' has been created.")
        except sa.exc.OperationalError as err:
            logger.warning(f"{type(err)}: Table '{cls.__tablename__}' already exists!")

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
            chosen_cols = cls.get_non_keys(as_str=False, allow_foreign=True)

            if filtrate is None:
                query = session.query(
                    *chosen_cols
                ).order_by(
                    *chosen_cols
                )

            else:
                query = session.query(
                    *chosen_cols
                ).filter(
                    sa.text(filtrate)
                ).order_by(
                    *chosen_cols
                )

        df = pd.read_sql(query.statement, session.bind, dtype=object)[:limit]
        df.insert(0, 'id', pd.Series(range(1, len(df) + 1)))
        return df

    @classmethod
    def show_table(cls,
                   dataframe: pd.DataFrame,
                   show_title: bool = False
                   ) -> figure.Figure:
        """The method return the table matplotlib figure.

        Args:
            dataframe (Optional[pd.DataFrame]): Defaults to None. Accepts the Pandas dataframe.
            show_title (bool): Defaults to False. Accepts the title of the table.
        Returns:
            figure.Figure: Matplotlib figure object.

        """
        figsize_x = len(dataframe.columns) + 1
        figsize_y = (len(dataframe.index) + 1) * 0.4
        fig = figure.Figure(figsize=(figsize_x, figsize_y))
        ax = fig.canvas.figure.subplots(1, 1)
        ax.axis('off')
        if show_title:
            ax.set_title(cls.__tablename__.title())
        table = ax.table(
            cellText=dataframe.values, colLabels=dataframe.columns,
            loc='center', cellLoc='center', bbox=[0, 0, 1, 1]
        )
        table.auto_set_column_width(col=list(range(len(dataframe.columns))))
        fig.tight_layout()

        return fig

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
            PowerNominal.insert_table([
                {'id': 1, 'power': 25}, {'id':9, 'power': 1000}
            ]) or
            PowerNominal.insert_table(DATA_DIR/'power')

        """
        if all((data is None, from_csv is None)):
            msg = 'Requires at least one not NoneType argument!'
            logger.error(msg)
            raise ValueError(msg)
        if from_csv:
            data = BaseMixin.__csv_to_list_of_dicts(from_csv)
        with session_scope() as session:
            result = session.connection().execute(sa.insert(cls), data).rowcount
            logger.warning(f"Table '{cls.__tablename__}' has been updated. {result} string(s) were inserted.")

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
                PowerNominals.update_table([
                    {'id': 1, 'power': 25}, {'id':9, 'power': 1000}]
                )

            for 'with_alias' method:
                Transformer.update_table({'vol_id': 2, 'power_id': 10}, options='with_alias',
                                            attr='voltage_id', alias='vol_id')
            for 'where_conditions' method:
                Transformer.update_table({'power': 630}, options='where_condition', attr='power', criteria=[250, 400])

        """

        def __primary_keys():
            with session_scope() as session:
                session.execute(sa.update(cls), data)

            return len(data)

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

        logger.warning(f"Table '{cls.__tablename__}' has been updated. {methods[options]()} matches found!")

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
            logger.warning(f"Rows were deleted from table '{cls.__tablename__}'. {rows_deleted} matches found!")

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
                    logger.warning(f"Table '{cls.__tablename__}' has been deleted.")

                else:

                    # MySQL dialect
                    if config_manager('DB_EXISTING_CONNECTION') == 'MySQL':
                        with session_scope(False) as session:
                            session.execute(sa.text(f'SET FOREIGN_KEY_CHECKS = 0;'))
                            session.execute(sa.text(f'DROP TABLE {cls.__tablename__};'))
                            session.execute(sa.text(f'SET FOREIGN_KEY_CHECKS = 1'))

                    # SQLite dialect
                    if config_manager('DB_EXISTING_CONNECTION') == 'SQLite':
                        with session_scope(False) as session:
                            session.execute(sa.text(f'PRAGMA FOREIGN_KEYS = OFF;'))
                            session.execute(sa.text(f'DROP TABLE {cls.__tablename__};'))
                            session.execute(sa.text(f'PRAGMA FOREIGN_KEYS = ON'))

                    logger.warning(f"Table '{cls.__tablename__}' has been forced deleted.")
            else:
                logger.error(f"Table '{cls.__tablename__}' has not been deleted. Deleting not confirmed.")
                raise

        except sa.exc.OperationalError as err:
            if 'Unknown table' in err.orig.__str__() or 'no such table' in err.orig.__str__():
                logger.info(f"There is no need to delete the table '{cls.__tablename__}', it does not exist")
            else:
                logger.error(err)

    @classmethod
    def reset_id(cls) -> None:
        """The method reset id order for the table with updating in child tables."""

        # MySQL dialect
        if config_manager('DB_EXISTING_CONNECTION') == 'MySQL':
            with session_scope(False) as session:
                session.execute(sa.text(f'SET @count = 0;'))
                session.execute(
                    sa.text(
                        f'UPDATE {cls.__tablename__} SET {cls.__tablename__}.id = @count:= @count + 1;')
                )
                session.execute(sa.text(f'ALTER TABLE {cls.__tablename__} AUTO_INCREMENT = 1'))

            logger.warning(f"Id order for table '{cls.__tablename__}' has been reset!")

        # SQLite dialect
        if config_manager('DB_EXISTING_CONNECTION') == 'SQLite' and JoinedMixin not in cls.__mro__:
            logger.error(
                f"In 'SQLite' DB resetting the parent table's ('{cls.__tablename__}') "
                'primary key is not available due to future relationship breakdowns '
                'between the parent and child tables. Use only child tables.'
            )

    @classmethod
    def get_all_keys(cls, as_str: bool = True) \
            -> ty.Union[tuple, ty.Tuple[str, sa.orm.attributes.InstrumentedAttribute]]:
        """The method generates all columns for the table.

        Args:
            as_str (bool, optional): Defaults to True. Accepts name string format for columns.
        Returns:
            Union[tuple, Tuple[str, sa.orm.attributes.InstrumentedAttribute]]:
            Returns the columns as names strings or as ORM objects.

        """
        all_keys = tuple(inspect(cls).columns.keys())

        if as_str:
            return all_keys
        else:
            return tuple(map(lambda x: getattr(cls, x), all_keys))

    @classmethod
    def get_primary_key(cls, as_str: bool = True) \
            -> ty.Union[str, sa.orm.InstrumentedAttribute]:
        """The method generates primary key column for the table.

        Args:
            as_str (bool, optional): Defaults to True. Accepts name string format for columns.
        Returns:
            Union[str, sa.orm.InstrumentedAttribute]: Returns the primary key column
            as name string or as ORM object.

        """
        primary_key = next(key.name for key in inspect(cls).primary_key)

        if as_str:
            return primary_key
        else:
            return getattr(cls, primary_key)

    @classmethod
    def get_foreign_keys(cls, on_side: bool = False, as_str: bool = True) \
            -> ty.Union[str, tuple, sa.orm.InstrumentedAttribute,
                        ty.Tuple[str, sa.orm.InstrumentedAttribute]]:
        """The method generates foreign keys columns for the table.

        Args:
            as_str (bool, optional): Defaults to True. Accepts name string format for columns.
            on_side (bool, optional): Defaults to False. Accept return foreign key from bind table.
        Returns:
            Union[str, tuple, sa.orm.InstrumentedAttribute,
                  ty.Tuple[str, sa.orm.InstrumentedAttribute]]: Returns the foreign keys columns
            as name strings or as ORM objects.

        """
        foreign_keys = None

        if not on_side:
            foreign_keys = tuple(
                key['constrained_columns'][0] for key
                in inspect(engine).get_foreign_keys(cls.__tablename__)
            )

        else:
            for table in Base.metadata.tables:
                for key in inspect(engine).get_foreign_keys(table):
                    if key['referred_table'] == cls.__tablename__ \
                            and key['referred_columns'][0] == cls.get_primary_key():
                        foreign_keys = key['constrained_columns'][0]

        if foreign_keys is None:
            return tuple()

        if as_str:
            return foreign_keys

        else:
            if isinstance(foreign_keys, str):
                for table in Base.metadata.tables:
                    table_class = cls.get_class_from_tablename(table)
                    if hasattr(table_class, foreign_keys):
                        return getattr(table_class, foreign_keys)

            if isinstance(foreign_keys, tuple):
                for table in Base.metadata.tables:
                    table_class = cls.get_class_from_tablename(table)
                    if all(map(lambda x: hasattr(table_class, x), foreign_keys)):
                        return tuple(map(lambda x: getattr(table_class, x), foreign_keys))

    @classmethod
    def get_non_keys(cls, as_str: bool = True, allow_foreign: bool = False) \
            -> ty.Union[tuple, ty.Union[str, sa.orm.InstrumentedAttribute]]:
        """The method generates not keys columns for the table.

        Args:
            as_str (bool, optional): Defaults to True. Accepts name string format for columns.
            allow_foreign (bool, optional): Defaults to False. Accept include foreign keys in result.
        Returns:
            Union[tuple, Union[str, sa.orm.InstrumentedAttribute]]:
            Returns the not keys columns as name strings or as ORM objects (and foreign keys if allowed).

        """
        if allow_foreign:
            non_keys = tuple(
                col for col in cls.get_all_keys() if
                col not in cls.get_primary_key()
            )

        else:
            non_keys = tuple(
                col for col in cls.get_all_keys() if
                col not in ((cls.get_primary_key(),) + cls.get_foreign_keys())
            )

        if as_str:
            return non_keys
        else:
            return tuple(getattr(cls, key) for key in non_keys)

    @staticmethod
    def get_class_from_tablename(tablename: str) -> Base.metadata:
        """
        The method returns table ORM class from table name.

        Args:
            tablename (str): Accept table name as string.
        Returns:
            Base.metadata: Returns table ORM class.

        """
        for c in Base.__subclasses__():
            if c.__tablename__ == tablename:
                return c

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
            cls.__new_name = name
        return cls.__new_name

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


class JoinedMixin:
    @classmethod
    def get_join_stmt(cls: BT) -> sa.sql.Join:
        """
        The method returns joined table statement.

        Returns:
            sa.sql.Join: Joined table statement.
        Example:
            print(Transformer.get_join_stmt()) ->

            'transformer
                JOIN power_nominal ON power_nominal.id = transformer.power_id
                JOIN voltage_nominal ON voltage_nominal.id = transformer.voltage_id
                JOIN scheme ON scheme.id = transformer.vector_group_id'

        """
        join_stmt = sa.join(cls, cls.SUBTABLES[0])
        for table in cls.SUBTABLES[1:]:
            join_stmt = join_stmt.join(table)
        return join_stmt

    @classmethod
    def read_joined_table(cls: BT) -> pd.DataFrame:
        """The method returns joined table as pandas DataFrame.

        Method returns joined table as pandas DataFrame with generated id columns.

        Returns:
            pd.DataFrame: Joined table as pandas DataFrame.
        Note:
            Further on the project, the joined table is a summary table of several source
            tables and the object of their association with additional information.

        """
        joined_tables_non_keys = tuple(
            map(lambda x: x.get_non_keys(as_str=False)[0], cls.SUBTABLES)
        )

        chosen_cols = (
            *joined_tables_non_keys, *cls.get_non_keys(as_str=False)
        )

        join_stmt = cls.get_join_stmt()

        with session_scope() as session:
            query = session.query(
                *chosen_cols
            ).select_from(
                join_stmt
            ).order_by(
                *joined_tables_non_keys
            )

            df = pd.read_sql(query.statement, session.bind, dtype=object)
            df.insert(0, 'id', pd.Series(range(1, len(df) + 1)))
            return df

    @classmethod
    def insert_joined_table(cls: BT, data: ty.List[dict]) -> None:
        """The method inserts new string into joined table.

        The method inserts new string into joined table. First, unique results are
        inserted into the source tables, then record id are extracted from the sources,
        which, along with other parameters, are added to the association object (joined table).

        Args:
            data (List[dict]): List of dictionaries with pairs "column name - value".
        Note:
            For correct insert query must contain all not empty fields of joined table row.
            List type need for package insert method.
        Example:
            Transformer.insert_joined_table(
                [
                    {
                        'power': 6300,
                        'voltage': 0.4,
                        'vector_group': 'У/Ун-0',
                        'power_short_circuit': 0.11,
                        'voltage_short_circuit': 0.22,
                        'resistance_r1': 0.333,
                        'reactance_x1': 0.444,
                        'resistance_r0': 0.555,
                        'reactance_x0': 0.777
                    }
                ]
            )

        """
        def __temp_insert(tab: BT, attr: str) -> None:
            """
            The method insert new string into source table.

            Args:
                attr (str): Not primary key column name.

            """
            session.connection().execute(sa.insert(
                tab
            ), [
                {attr: row[attr]}
            ])

        with session_scope() as session:
            for row in data:

                attrs = {}

                for table in cls.SUBTABLES:
                    for col_name in table.get_non_keys():
                        try:
                            __temp_insert(table, col_name)
                            __temp_insert.unique = True
                        except sa.exc.IntegrityError as err:
                            if 'Duplicate entry' in err.orig.__str__():
                                pass

                        attrs[table.get_foreign_keys(on_side=True)] = session.query(table).filter(
                            getattr(table, col_name) == row[col_name]
                        ).first().id

                if hasattr(__temp_insert, 'unique'):
                    result = session.connection().execute(sa.insert(
                        cls
                    ), [
                        {
                            **attrs,
                            **{k: v for k, v in row.items() if k not in attrs}
                        }
                    ]).rowcount
                    print(f"Joined table '{cls.__tablename__}' has been updated. {result} string(s) were inserted.")

                else:
                    print(f"Joined table '{cls.__tablename__}' not updated. 0 unique string or another problem.")

    @classmethod
    def update_joined_table(cls: BT,
                            old_source_data: dict = None,
                            new_source_data: dict = None,
                            target_row_data: dict = None
                            ) -> None:
        """The method updates rows into joined table (and source if necessary).

        Args:
            old_source_data (dict): Existing source attribute pairs "column name - value".
            new_source_data (dict): New source attribute pairs "column name - value".
            target_row_data (dict): New joined table attribute pairs "column name - value".
        Note:
            First insert target row data into joined table.
            Then, if necessary, updated source rows.
        Example:
            Transformer.update_joined_table(
                old_source_data={
                    'voltage': 0.4,
                    'power': 100,
                    'vector_group': 'У/Ун-0'
                }, \n
                new_source_data={
                    'vector_group': 'У/Z-0',
                    'power': 6300
                }, \n
                target_row_data={
                    'power_short_circuit': 0.11,
                    'voltage_short_circuit': 0.22,
                    'resistance_r1': 0.333,
                    'reactance_x1': 0.444,
                    'resistance_r0': 0.555,
                    'reactance_x0': 0.777
                }
            )

        """
        old_source_dict = None
        __UPDATED = []

        if old_source_data:
            old_source_dict = {
                getattr(table, attr): old_source_data[attr]
                for table in cls.SUBTABLES
                for attr in old_source_data
                if hasattr(table, attr)
            }

            with session_scope() as session:
                primary_key_queries = (
                    session.query(table.id).filter(relation[0] == relation[1])
                    for table, relation in zip(cls.SUBTABLES, old_source_dict.items())
                )

        # Update one string in joined table (update non_keys cols)
        if old_source_data and target_row_data:
            with session_scope() as session:
                query = session.query(
                    cls
                ).filter(
                    sa.and_(
                        key == query.as_scalar()
                        for key, query in zip(
                            cls.get_foreign_keys(as_str=False), primary_key_queries
                        )
                    )
                ).update(
                    {
                        getattr(cls, k): v
                        for k, v in target_row_data.items()
                        if v
                    }
                )

            __UPDATED.append(query)

        # Update source tables strings (update non_keys cols in source tables)
        if old_source_data and new_source_data:

            new_source_dict = {
                getattr(table, attr): new_source_data[attr]
                for table in cls.SUBTABLES
                for attr in new_source_data
                if hasattr(table, attr)
            }

            changed_tables = tuple(
                table
                for table in cls.SUBTABLES
                for attr in new_source_data
                if hasattr(table, attr)
            )

            for source_table in changed_tables:
                source_attr = source_table.get_non_keys()[0]

                with session_scope() as session:
                    query = session.query(
                        source_table
                    ).filter(
                        getattr(source_table, source_attr) == old_source_dict[getattr(source_table, source_attr)]
                    ).update(
                        {
                            source_attr: new_source_dict[getattr(source_table, source_attr)]
                        }
                    )

                __UPDATED.append(query)

        if __UPDATED:
            logger.warning(f"Joined table '{cls.__tablename__}' has been changed. "
                           f"{sum(__UPDATED)} record(s) in joined and source tables were updated.")

        else:
            logger.error(f"Joined table '{cls.__tablename__}' not updated. "
                         'Uncorrected / empty query or another problem.')

    @classmethod
    def delete_joined_table(cls: BT,
                            source_data=None,
                            from_source: bool = False
                            ) -> None:
        """The method deletes rows into joined table (and source if necessary).

        Args:
            source_data (dict): Existing source attribute pairs "column name - value".
            from_source (bool): If True, deletes rows from source table, otherwise from joined table.
        Note:
            Default delete single rows from joined table.
        Example:
            Transformer.delete_joined_table(
                source_data={
                    'voltage': 0.4,
                    'vector_group': 'У/Ун-0',
                    'power': 100
                }, \n
                from_source=True
            )

        """
        source_dict = None
        __DELETED = None

        if source_data:
            source_dict = {
                getattr(table, attr): source_data[attr]
                for table in cls.SUBTABLES
                for attr in source_data
                if hasattr(table, attr)
            }

            with session_scope() as session:
                primary_key_queries = (
                    session.query(table.id).filter(relation[0] == relation[1])
                    for table, relation in zip(cls.SUBTABLES, source_dict.items())
                )

        # Delete one string in joined table
        if source_data and not from_source:
            with session_scope() as session:
                query = session.query(
                    cls
                ).filter(
                    sa.and_(
                        key == query.as_scalar()
                        for key, query in zip(
                            cls.get_foreign_keys(as_str=False), primary_key_queries
                        )
                    )
                ).delete()

            __DELETED = True
            logger.warning(f"Joined table '{cls.__tablename__}' has been changed. "
                           f"{query} record(s) from joined table were deleted.")

        # Delete source tables strings
        if source_data and from_source:

            changed_tables = tuple(
                table
                for table in cls.SUBTABLES
                for attr in source_data
                if hasattr(table, attr)
            )

            for source_table in changed_tables:
                source_attr = source_table.get_non_keys()[0]

                with session_scope() as session:
                    query = session.query(
                        source_table
                    ).filter(
                        getattr(source_table, source_attr) == source_dict[getattr(source_table, source_attr)]
                    ).delete()

            __DELETED = True
            logger.warning(f"Joined table '{cls.__tablename__}' has been changed. "
                           f"{query} record(s) from source tables were deleted.")

        if not __DELETED:
            logger.error(f"Joined table '{cls.__tablename__}' not updated. "
                         'Uncorrected / empty query or another problem.')

    @classmethod
    def reset_id(cls: BT) -> None:
        """The method extends 'reset_id' method from class 'BaseMixin'.

        This part of parent method allows to reset id order for joined table in SQLite DB.

        """
        super(JoinedMixin, cls).reset_id()

        # SQL dialect
        if config_manager('DB_EXISTING_CONNECTION') == 'SQLite':
            with session_scope(False) as session:
                select_cols = session.query(
                    *cls.get_non_keys(as_str=False, allow_foreign=True)
                ).statement

                df = pd.read_sql(select_cols, session.bind, dtype=object)

                session.execute(sa.text(f'DELETE FROM {cls.__tablename__};'))
                session.execute(sa.text(f"UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = '{cls.__tablename__}';"))

            df.to_sql(f'{cls.__tablename__}', engine, if_exists='append', index=False)

            logger.warning(f"Id order for joined table '{cls.__tablename__}' has been reset!")
