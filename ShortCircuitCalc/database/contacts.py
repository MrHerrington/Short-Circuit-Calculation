# -*- coding: utf-8 -*-
"""The module contains ORM models of tables with equipment
of the category 'contacts and other resistances'"""


import sqlalchemy as sa
import sqlalchemy.orm
from ShortCircuitCalc.tools import Base
from ShortCircuitCalc.database import BaseMixin


class Device(BaseMixin, Base):
    """The class describes a table of switching devices.

    Describes a table of switching devices: automatic current breaker, switches, etc.

    """
    device_type = sa.orm.mapped_column(sa.String(25), nullable=False, unique=True, sort_order=10)

    # relationships
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='devices')


class CurrentNominal(BaseMixin, Base):
    """The class describes a table of the switching devices current nominals"""
    current_value = sa.orm.mapped_column(sa.Integer, nullable=False, unique=True, sort_order=10)

    # relationships
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='current_nominals')


class CurrentBreaker(BaseMixin, Base):
    """The class describes a table of the switching devices.

    Describes a table of the switching devices, it's device type id, current value id, resistances.

    """
    device_type_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(Device.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    current_value_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(CurrentNominal.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10)
    resistance_r1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    reactance_x1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=True, default=0, sort_order=10)
    resistance_r0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=True, default=0, sort_order=10)
    reactance_x0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=True, default=0, sort_order=10)

    # relationships
    devices = sa.orm.relationship('Device', back_populates='current_breakers')
    current_nominals = sa.orm.relationship('CurrentNominal', back_populates='current_breakers')


class OtherContact(BaseMixin, Base):
    """The class describes a table of the others resistances."""
    contact_type = sa.orm.mapped_column(sa.String(25), nullable=False, unique=True, sort_order=10)
    resistance_r1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=False, sort_order=10)
    reactance_x1 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=True, default=0, sort_order=10)
    resistance_r0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=True, default=0, sort_order=10)
    reactance_x0 = sa.orm.mapped_column(sa.Numeric(8, 5), nullable=True, default=0, sort_order=10)
