import json
import sqlalchemy as sa
import sqlalchemy.orm


def db_access() -> str:

    def keys_getter() -> str:
        with open('db_security.json', 'r', encoding='UTF-8') as file:
            temp = json.load(file)['db_access']
            login, password, db_name = temp['login'], temp['password'], temp['db_name']
            db_access.engine_string = f"mysql+pymysql://{login}:{password}@localhost/{db_name}?charset=utf8mb4"
        return db_access.engine_string

    try:
        return db_access.engine_string
    except AttributeError:
        keys_getter()
        return db_access.engine_string


class Base(sa.orm.DeclarativeBase):
    pass


# Субтаблицы с параметрами трансформаторов
# Таблица номинальных мощностей трансформаторов
class PowerNominal(Base):
    __tablename__ = 'power_nominal'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    power = sa.Column(sa.Integer, nullable=False)
    transformers = sa.orm.relationship('Transformer', back_populates='power_nominals')


# Таблица номинальных напряжений трансформаторов
class VoltageNominal(Base):
    __tablename__ = 'voltage_nominal'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    voltage = sa.Column(sa.Numeric(1, 1), nullable=False)
    transformers = sa.orm.relationship('Transformer', back_populates='voltage_nominals')


# Таблица групп соединений обмоток трансформаторов
class Scheme(Base):
    __tablename__ = 'scheme'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    vector_group = sa.Column(sa.String(10))
    transformers = sa.orm.relationship('Transformer', back_populates='schemes')


# Таблица связи по трансформаторам с мощностью потерь и напряжением короткого замыкания
class Transformer(Base):
    __tablename__ = 'transformer'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    Snom_id = sa.Column(sa.Integer, sa.ForeignKey(PowerNominal.id, ondelete='CASCADE'))
    Unom_id = sa.Column(sa.Integer, sa.ForeignKey(VoltageNominal.id, ondelete='CASCADE'))
    scheme_id = sa.Column(sa.Integer, sa.ForeignKey(Scheme.id, ondelete='CASCADE'))
    power_short_circuit = sa.Column(sa.Numeric(2, 2), nullable=False)
    voltage_short_circuit = sa.Column(sa.Numeric(1, 1), nullable=False)
    power_nominals = sa.orm.relationship('PowerNominal', back_populates='transformers')
    voltage_nominals = sa.orm.relationship('VoltageNominal', back_populates='transformers')
    schemes = sa.orm.relationship('Scheme', back_populates='transformers')





class Cable:
    __tablename__ = 'cable'

engine = sa.create_engine(db_access(), echo=True)
Base.metadata.create_all(engine)
