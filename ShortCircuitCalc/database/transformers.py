# -*- coding: utf-8 -*-
"""The module contains ORM models of tables with equipment
of the category 'transformers'"""


import sqlalchemy as sa
import sqlalchemy.orm
import pandas as pd

from ShortCircuitCalc.tools import Base, session_scope
from ShortCircuitCalc.database.mixins import BaseMixin, JoinedMixin


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


class Transformer(JoinedMixin, BaseMixin, Base):
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
