import sqlalchemy as sa
import sqlalchemy.orm
from tools import Base
from database import BaseMixin


# Субтаблицы с параметрами трансформаторов
# Таблица номинальных мощностей трансформаторов
class PowerNominal(BaseMixin, Base):
    power = sa.orm.mapped_column(sa.Integer, nullable=False, unique=True, sort_order=10)
    transformers = sa.orm.relationship('Transformer', back_populates='power_nominals')


# Таблица номинальных напряжений трансформаторов
class VoltageNominal(BaseMixin, Base):
    voltage = sa.orm.mapped_column(sa.Numeric(1, 1), nullable=False, unique=True, sort_order=10)
    transformers = sa.orm.relationship('Transformer', back_populates='voltage_nominals')


# Таблица групп соединений обмоток трансформаторов
class Scheme(BaseMixin, Base):
    vector_group = sa.orm.mapped_column(sa.String(10), nullable=False, unique=True, sort_order=10)
    transformers = sa.orm.relationship('Transformer', back_populates='schemes')


# Таблица связи по трансформаторам с мощностью потерь, напряжением короткого замыкания,
# сопротивлениями и реактансами прямой и обратной последовательностей
class Transformer(BaseMixin, Base):
    power_id = sa.orm.mapped_column(sa.Integer, sa.ForeignKey(PowerNominal.id, ondelete='CASCADE'), sort_order=10)
    voltage_id = sa.orm.mapped_column(sa.Integer, sa.ForeignKey(VoltageNominal.id, ondelete='CASCADE'), sort_order=10)
    vector_group_id = sa.orm.mapped_column(sa.Integer, sa.ForeignKey(Scheme.id, ondelete='CASCADE'), sort_order=10)
    # power_short_circuit = sa.orm.mapped_column(sa.Numeric(2, 2), nullable=False, sort_order=10)
    # voltage_short_circuit = sa.orm.mapped_column(sa.Numeric(1, 1), nullable=False, sort_order=10)
    # resistance_r1 = sa.orm.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)
    # reactance_x1 = sa.orm.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)
    # resistance_r0 = sa.orm.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)
    # reactance_x0 = sa.orm.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)
    power_nominals = sa.orm.relationship('PowerNominal', back_populates='transformers')
    voltage_nominals = sa.orm.relationship('VoltageNominal', back_populates='transformers')
    schemes = sa.orm.relationship('Scheme', back_populates='transformers')


if __name__ == '__main__':
    PowerNominal.create_table()
    VoltageNominal.create_table()
    Scheme.create_table()
    Transformer.create_table()
    # PowerNominal.drop_table(PowerNominal.__tablename__)
    # VoltageNominal.drop_table(VoltageNominal.__tablename__)
    # Scheme.drop_table(Scheme.__tablename__)
    # Transformer.drop_table(Transformer.__tablename__)
    pass
