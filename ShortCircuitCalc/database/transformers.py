# -*- coding: utf-8 -*-
"""The module contains ORM models of tables with equipment
of the category 'transformers'"""


from collections import namedtuple

import sqlalchemy as sa
import sqlalchemy.orm
from sqlalchemy.inspection import inspect
import pandas as pd

from ShortCircuitCalc.tools import Base, session_scope
from ShortCircuitCalc.database.mixins import BaseMixin


__all__ = ('PowerNominal', 'VoltageNominal', 'Scheme', 'Transformer')


class PowerNominal(BaseMixin, Base):
    """The class describes a table of transformer power nominals"""
    power = sa.orm.mapped_column(sa.Integer, nullable=False, unique=True, sort_order=10)

    # relationships
    transformers = sa.orm.relationship('Transformer', back_populates='power_nominals')


class VoltageNominal(BaseMixin, Base):
    """The class describes a table of transformer voltage nominals"""
    voltage = sa.orm.mapped_column(sa.Numeric(6, 3), nullable=False, unique=True, sort_order=10)

    # relationships
    transformers = sa.orm.relationship('Transformer', back_populates='voltage_nominals')


class Scheme(BaseMixin, Base):
    """The class describes a table of transformer vector group schemes"""
    vector_group = sa.orm.mapped_column(sa.String(10), nullable=False, unique=True, sort_order=10)

    # relationships
    transformers = sa.orm.relationship('Transformer', back_populates='schemes')


class Transformer(BaseMixin, Base):
    """The class describes a table of communication by transformers.

    Describes a table of communication by transformers, values of short circuit current
    powers and voltages, resistance and reactance of forward and reverse sequences.

    """

    SUBTABLES = PowerNominal, VoltageNominal, Scheme

    power_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(PowerNominal.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    voltage_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(VoltageNominal.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    vector_group_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(Scheme.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    power_short_circuit = sa.orm.mapped_column(sa.Numeric(6, 3), nullable=False, sort_order=10)
    voltage_short_circuit = sa.orm.mapped_column(sa.Numeric(6, 3), nullable=False, sort_order=10)
    resistance_r1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    reactance_x1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    resistance_r0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    reactance_x0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)

    # relationships
    power_nominals = sa.orm.relationship('PowerNominal', back_populates='transformers')
    voltage_nominals = sa.orm.relationship('VoltageNominal', back_populates='transformers')
    schemes = sa.orm.relationship('Scheme', back_populates='transformers')

    @classmethod
    def read_joined_table(cls) -> pd.DataFrame:
        with session_scope() as session:
            query = session.query(
                PowerNominal.power,
                VoltageNominal.voltage,
                Scheme.vector_group,
                cls.power_short_circuit,
                cls.voltage_short_circuit,
                cls.resistance_r1,
                cls.reactance_x1,
                cls.resistance_r0,
                cls.reactance_x0
            ).select_from(
                cls
            ).join(
                PowerNominal, cls.power_id == PowerNominal.id
            ).join(
                VoltageNominal, cls.voltage_id == VoltageNominal.id
            ).join(
                Scheme, cls.vector_group_id == Scheme.id
            ).order_by(
                PowerNominal.power,
                VoltageNominal.voltage,
                Scheme.vector_group
            )

            df = pd.read_sql(query.statement, session.bind, dtype=object)
            df.insert(0, 'id', pd.Series(range(1, len(df) + 1)))
            return df

    @classmethod
    def insert_joined_table(cls, data) -> None:

        def __temp_row(tab, attr: str) -> None:
            session.connection().execute(sa.insert(
                tab
            ), [
                {attr: row[attr]}
            ])

        with session_scope() as session:
            for row in data:

                attrs = {}

                for table in cls.SUBTABLES:
                    non_keys_cols = [
                        col for col in inspect(table).columns.keys() if
                        col not in [key.name for key in inspect(table).primary_key]
                    ]

                    Link = namedtuple('Link', ('table', 'attr'))
                    link = Link(table, *non_keys_cols)

                    try:
                        __temp_row(link.table, link.attr)
                        __temp_row.unique = True
                    except sa.exc.IntegrityError as err:
                        if 'Duplicate entry' in err.orig.__str__():
                            pass

                    attrs[link.attr + '_id'] = session.query(table).filter(
                        getattr(table, link.attr) == row[link.attr]
                    ).first().id

                if hasattr(__temp_row, 'unique'):
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
