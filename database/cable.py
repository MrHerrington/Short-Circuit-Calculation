# -*- coding: utf-8 -*-
"""The module contains ORM models of tables with equipment
of the category 'cables and wires'"""


import sqlalchemy as sa
import sqlalchemy.orm
from tools import Base
from database import BaseMixin


class Mark(BaseMixin, Base):
    """The class describes a table of cable marking types"""
    mark_name = sa.mapped_column(sa.String(20), nullable=False, unique=True, sort_order=10)

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='marks')


class Amount(BaseMixin, Base):
    """The class describes a table of the number of conductive cores of cables"""
    multicore_amount = sa.mapped_column(sa.Integer, nullable=False, unique=True, sort_order=10)

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='amounts')


class Range(BaseMixin, Base):
    """The class describes a table of cable ranges"""
    cable_range = sa.mapped_column(sa.Numeric(3, 2), nullable=False, unique=True, sort_order=10)

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='ranges')


class Cable(BaseMixin, Base):
    """The class describes a table of communication by cables.

    Describes a table of communication by cables, permissible values of long-term flowing
    current, resistance and reactance of forward and reverse sequences.

    """
    mark_name_id = sa.mapped_column(sa.Integer, sa.ForeignKey(Mark.id, ondelete='CASCADE'), sort_order=10)
    multicore_amount_id = sa.mapped_column(sa.Integer, sa.ForeignKey(Amount.id, ondelete='CASCADE'), sort_order=10)
    cable_range_id = sa.mapped_column(sa.Integer, sa.ForeignKey(Range.id, ondelete='CASCADE'), sort_order=10)
    continuous_current = sa.mapped_column(sa.Numeric(3, 2), nullable=False, sort_order=10)
    resistance_r1 = sa.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)
    reactance_x1 = sa.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)
    resistance_r0 = sa.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)
    reactance_x0 = sa.mapped_column(sa.Numeric(5, 5), nullable=False, sort_order=10)

    # relationships
    marks = sa.orm.relationship('Mark', back_populates='cables')
    amounts = sa.orm.relationship('Amount', back_populates='cables')
    ranges = sa.orm.relationship('Range', back_populates='cables')
