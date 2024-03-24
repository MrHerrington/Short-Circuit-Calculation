from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship


def db_access():
    with open('DB_security.txt', 'r', encoding='UTF-8') as file:
        login, password, db_name = file.read().splitlines()
    return f"mysql+pymysql://{login}:{password}@localhost/{db_name}?charset=utf8mb4"


class Base(DeclarativeBase):
    pass


# # Типы продукции: трансформатор, кабель, автомат, рубильник, etc
# class Product(Base):
#     __tablename__ = 'product'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     product_type = Column(String)


# Субтаблицы с параметрами трансформаторов
# Таблица номинальных мощностей трансформаторов
class PowerNominal(Base):
    __tablename__ = 'power_nominal'
    id = Column(Integer, primary_key=True, autoincrement=True)
    power_nominal = Column(Integer, nullable=False)
    transformers = relationship('transformers', back_populates='power_nominals')


# Таблица номинальных напряжений трансформаторов
class VoltageNominal(Base):
    __tablename__ = 'voltage_nominal'
    id = Column(Integer, primary_key=True, autoincrement=True)
    voltage_nominal = Column(Numeric(1, 1), nullable=False)
    transformers = relationship('transformers', back_populates='voltage_nominals')


# Таблица групп соединений обмоток трансформаторов
class VectorGroup(Base):
    __tablename__ = 'vector_group'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vector_group = Column(String(10))
    transformers = relationship('transformers', back_populates='vector_groups')


# Таблица связи по трансформаторам с мощностью потерь и напряжением короткого замыкания
class Transformer(Base):
    __tablename__ = 'transformer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Snom_id = Column(Integer, ForeignKey(PowerNominal.id, ondelete='CASCADE'))
    Unom_id = Column(Integer, ForeignKey(VoltageNominal.id, ondelete='CASCADE'))
    vector_group_id = Column(Integer, ForeignKey(VectorGroup.id, ondelete='CASCADE'))
    power_short_circuit = Column(Numeric(2, 2), nullable=False)
    voltage_short_circuit = Column(Numeric(1, 1), nullable=False)
    power_nominals = relationship(PowerNominal.__tablename__, back_populates='transformers')
    voltage_nominals = relationship(VoltageNominal.__tablename__, back_populates='transformers')
    vector_groups = relationship(VectorGroup.__tablename__, back_populates='transformers')


engine = create_engine(db_access(), echo=True)
Base.metadata.create_all(engine)
