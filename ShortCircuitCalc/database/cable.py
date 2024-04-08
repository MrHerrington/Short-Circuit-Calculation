# -*- coding: utf-8 -*-
"""The module contains ORM models of tables with equipment
of the category 'cables and wires'"""


import sqlalchemy as sa
import sqlalchemy.orm
from ShortCircuitCalc.tools import Base
from ShortCircuitCalc.database import BaseMixin


class Mark(BaseMixin, Base):
    """The class describes a table of cable marking types"""
    mark_name = sa.orm.mapped_column(sa.String(20), nullable=False, unique=True, sort_order=10)

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='marks')


class Amount(BaseMixin, Base):
    """The class describes a table of the number of conductive cores of cables"""
    multicore_amount = sa.orm.mapped_column(sa.Integer, nullable=False, unique=True, sort_order=10)

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='amounts')


class RangeVal(BaseMixin, Base):
    """The class describes a table of cable ranges"""
    cable_range = sa.orm.mapped_column(sa.Numeric(4, 1), nullable=False, unique=True, sort_order=10)

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='ranges')


class Cable(BaseMixin, Base):
    """The class describes a table of communication by cables.

    Describes a table of communication by cables, permissible values of long-term flowing
    current, resistance and reactance of forward and reverse sequences.

    """
    mark_name_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(Mark.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    multicore_amount_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(Amount.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    cable_range_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(RangeVal.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    continuous_current = sa.orm.mapped_column(sa.Numeric(5, 2), nullable=False, sort_order=10)
    resistance_r1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    reactance_x1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    resistance_r0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    reactance_x0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)

    # relationships
    marks = sa.orm.relationship('Mark', back_populates='cables')
    amounts = sa.orm.relationship('Amount', back_populates='cables')
    ranges = sa.orm.relationship('RangeVal', back_populates='cables')
