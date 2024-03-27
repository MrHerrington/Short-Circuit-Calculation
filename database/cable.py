import sqlalchemy as sa
import sqlalchemy.orm
from tools import Base, engine


# Субтаблицы с параметрами кабелей / проводов
# Таблица типов маркировки кабелей
class Mark(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    mark_name = sa.Column(sa.String(20), nullable=False, unique=True)
    cables = sa.orm.relationship('Cable', back_populates='marks')


# Таблица количества токопроводящих жил кабелей
class Amount(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    multicore_amount = sa.Column(sa.Integer, nullable=False, unique=True)
    cables = sa.orm.relationship('Cable', back_populates='amounts')


# Таблица поперечных сечений кабелей
class Range(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    cable_range = sa.Column(sa.Numeric(3, 2), nullable=False, unique=True)
    cables = sa.orm.relationship('Cable', back_populates='ranges')


# Таблица связи по кабелям, допустимым величинам длительно протекающего тока,
# сопротивлениями и реактансами прямой и обратной последовательностей
class Cable(Base):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    mark_name_id = sa.Column(sa.Integer, sa.ForeignKey(Mark.id, ondelete='CASCADE'))
    multicore_amount_id = sa.Column(sa.Integer, sa.ForeignKey(Amount.id, ondelete='CASCADE'))
    cable_range_id = sa.Column(sa.Integer, sa.ForeignKey(Range.id, ondelete='CASCADE'))
    continuous_current = sa.Column(sa.Numeric(3, 2), nullable=False)
    resistance_r1 = sa.Column(sa.Numeric(5, 5), nullable=False)
    reactance_x1 = sa.Column(sa.Numeric(5, 5), nullable=False)
    resistance_r0 = sa.Column(sa.Numeric(5, 5), nullable=False)
    reactance_x0 = sa.Column(sa.Numeric(5, 5), nullable=False)
    marks = sa.orm.relationship('Mark', back_populates='cables')
    amounts = sa.orm.relationship('Amount', back_populates='cables')
    ranges = sa.orm.relationship('Range', back_populates='cables')


Base.metadata.create_all(engine)
