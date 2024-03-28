import sqlalchemy as sa
from sqlalchemy.orm import declared_attr
import sqlalchemy.exc
from tools import Base, engine, session_scope
from typing import Union, Callable
import re


def camel_to_snake(name: str) -> str:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class BaseMixin:
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)

    @declared_attr
    @classmethod
    def id(cls):
        return sa.orm.mapped_column(sa.Integer, primary_key=True, autoincrement=True, sort_order=0)

    @classmethod
    def create_table(cls) -> None:
        try:
            Base.metadata.tables[cls.__tablename__].create(engine)
            print(f"Table '{cls.__tablename__}' has been created.")
        except sa.exc.OperationalError as err:
            print(f"{type(err)}: Table '{cls.__tablename__}' already exists!")

    @classmethod
    def read_table(cls, col_name, *args, **kwargs) -> map:
        # noinspection PyArgumentList
        with session_scope() as session:
            request = session.query(cls).filter(cls.__getattribute__(cls, '%s' % col_name)).all()
        print(args)
        return map(lambda x: x.__getattribute__('%s' % col_name), request)

    @classmethod
    def drop_table(cls, confirm: Union[Callable, str, None] = None) -> None:
        try:
            if confirm == cls.__tablename__:
                Base.metadata.tables[cls.__tablename__].drop(engine)
                print(f"Table '{cls.__tablename__}' has been deleted.")
            else:
                raise f"Table '{cls.__tablename__}' deletion not confirmed."
        except sa.exc.OperationalError as err:
            raise err from None
