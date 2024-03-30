import sqlalchemy as sa
from sqlalchemy.orm import declared_attr
import sqlalchemy.exc
from tools import Base, engine, session_scope
import typing as ty
import re
import pandas as pd
from tabulate import tabulate


class BaseMixin:
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return BaseMixin.__camel_to_snake(cls.__name__)

    @declared_attr
    @classmethod
    def id(cls) -> sa.orm.mapped_column:
        return sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True, sort_order=0)

    @classmethod
    def create_table(cls) -> None:
        try:
            Base.metadata.tables[cls.__tablename__].create(engine)
            print(f"Table '{cls.__tablename__}' has been created.")
        except sa.exc.OperationalError as err:
            print(f"{type(err)}: Table '{cls.__tablename__}' already exists!")

    @classmethod
    def read_table(cls, filtrate: ty.Optional[str] = None, limit: ty.Optional[int] = None) -> pd.DataFrame:
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
        df = cls.read_table(filtrate=filtrate, limit=limit)
        print(tabulate(df, headers='keys', tablefmt='psql', showindex=indexes))

    @classmethod
    def insert_table(cls, data: ty.List[dict]) -> None:
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
        for attr in cls.__getattribute__(cls, '__table__').columns.keys():
            expression = re.sub(attr, 'cls.%s' % attr, expression)
        return expression

    @staticmethod
    def __camel_to_snake(name: str) -> str:
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
