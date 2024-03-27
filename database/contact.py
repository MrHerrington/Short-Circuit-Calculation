import sqlalchemy as sa
import sqlalchemy.orm
from tools import Base, engine


# Таблица типов коммутационных аппаратов: автоматы, рубильники, etc
class Device(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    device_type = sa.Column(sa.String(25), nullable=False, unique=True)
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='devices')


# Таблица токовых номиналов для коммутационных аппаратов
class CurrentNominal(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    current_value = sa.Column(sa.Integer, nullable=False, unique=True)
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='current_nominals')


# Таблица связи по коммутационным аппаратам с активными сопротивлениями
class CurrentBreaker(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    device_type_id = sa.Column(sa.Integer, sa.ForeignKey(Device.id, ondelete='CASCADE'))
    current_value_id = sa.Column(sa.Integer, sa.ForeignKey(CurrentNominal.id, ondelete='CASCADE'))
    resistance = sa.Column(sa.Numeric(5, 5), nullable=False)
    devices = sa.orm.relationship('Device', back_populates='current_breakers')
    current_nominals = sa.orm.relationship('CurrentNominal', back_populates='current_breakers')


class OtherContact(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    contact_type = sa.Column(sa.String(25), nullable=False, unique=True)
    resistance = sa.Column(sa.Numeric(5, 5), nullable=False)


Base.metadata.create_all(engine)
