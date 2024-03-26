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


# Таблица связи по трансформаторам с мощностью потерь, напряжением короткого замыкания,
# сопротивлениями и реактансами прямой и обратной последовательностей
class Transformer(Base):
    __tablename__ = 'transformer'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    power_id = sa.Column(sa.Integer, sa.ForeignKey(PowerNominal.id, ondelete='CASCADE'))
    voltage_id = sa.Column(sa.Integer, sa.ForeignKey(VoltageNominal.id, ondelete='CASCADE'))
    vector_group_id = sa.Column(sa.Integer, sa.ForeignKey(Scheme.id, ondelete='CASCADE'))
    power_short_circuit = sa.Column(sa.Numeric(2, 2), nullable=False)
    voltage_short_circuit = sa.Column(sa.Numeric(1, 1), nullable=False)
    resistance_r1 = sa.Column(sa.Numeric(2, 5), nullable=False)
    reactance_x1 = sa.Column(sa.Numeric(2, 5), nullable=False)
    resistance_r0 = sa.Column(sa.Numeric(2, 5), nullable=False)
    reactance_x0 = sa.Column(sa.Numeric(2, 5), nullable=False)
    power_nominals = sa.orm.relationship('PowerNominal', back_populates='transformers')
    voltage_nominals = sa.orm.relationship('VoltageNominal', back_populates='transformers')
    schemes = sa.orm.relationship('Scheme', back_populates='transformers')


# Субтаблицы с параметрами кабелей / проводов
# Таблица типов маркировки кабелей
class Mark(Base):
    __tablename__ = 'mark'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    mark_name = sa.Column(sa.String(20))
    cables = sa.orm.relationship('Cable', back_populates='marks')


# Таблица количества токопроводящих жил кабелей
class Amount(Base):
    __tablename__ = 'amount'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    multicore_amount = sa.Column(sa.Integer)
    cables = sa.orm.relationship('Cable', back_populates='amounts')


# Таблица поперечных сечений кабелей
class Range(Base):
    __tablename__ = 'range'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    cable_range = sa.Column(sa.Numeric(3, 2))
    cables = sa.orm.relationship('Cable', back_populates='ranges')


# Таблица связи по кабелям, допустимым величинам длительно протекающего тока,
# сопротивлениями и реактансами прямой и обратной последовательностей
class Cable(Base):
    __tablename__ = 'cable'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    mark_name_id = sa.Column(sa.Integer, sa.ForeignKey(Mark.id, ondelete='CASCADE'))
    multicore_amount_id = sa.Column(sa.Integer, sa.ForeignKey(Amount.id, ondelete='CASCADE'))
    cable_range_id = sa.Column(sa.Integer, sa.ForeignKey(Range.id, ondelete='CASCADE'))
    continuous_current = sa.Column(sa.Numeric(3, 2), nullable=False)
    resistance_r1 = sa.Column(sa.Numeric(2, 5), nullable=False)
    reactance_x1 = sa.Column(sa.Numeric(2, 5), nullable=False)
    resistance_r0 = sa.Column(sa.Numeric(2, 5), nullable=False)
    reactance_x0 = sa.Column(sa.Numeric(2, 5), nullable=False)
    marks = sa.orm.relationship('Mark', back_populates='cables')
    amounts = sa.orm.relationship('Amount', back_populates='cables')
    ranges = sa.orm.relationship('Range', back_populates='cables')


# Таблица типов коммутационных аппаратов: автоматы, рубильники, etc
class Device(Base):
    __tablename__ = 'device'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    device_type = sa.Column(sa.String(25))
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='devices')


# Таблица токовых номиналов для коммутационных аппаратов
class CurrentNominal(Base):
    __tablename__ = 'current_nominal'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    cable_range = sa.Column(sa.Integer)
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='current_nominals')


# Таблица связи по коммутационным аппаратам с активными сопротивлениями
class CurrentBreaker(Base):
    __tablename__ = 'current_breaker'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    device_type_id = sa.Column(sa.Integer, sa.ForeignKey(Device.id, ondelete='CASCADE'))
    cable_range_id = sa.Column(sa.Integer, sa.ForeignKey(CurrentNominal.id, ondelete='CASCADE'))
    resistance_r1 = sa.Column(sa.Numeric(2, 5), nullable=False)
    devices = sa.orm.relationship('Device', back_populates='current_breakers')
    current_nominals = sa.orm.relationship('CurrentNominal', back_populates='current_breakers')


engine = sa.create_engine(db_access(), echo=True)
Base.metadata.create_all(engine)
