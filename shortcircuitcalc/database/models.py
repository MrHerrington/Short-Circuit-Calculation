# -*- coding: utf-8 -*-
"""
The module contains ORM models of tables with equipment
of the categories 'transformers', 'cables and wires',
and 'contacts and other resistances'

"""


from decimal import Decimal
from dataclasses import dataclass, field

import sqlalchemy as sa
import sqlalchemy.orm

from shortcircuitcalc.tools import Base, Validator
from shortcircuitcalc.database.mixins import (
    BaseMixin, JoinedMixin
)


__all__ = (
    'PowerNominal', 'VoltageNominal', 'Scheme', 'Transformer',
    'Mark', 'RangeVal', 'Amount', 'Cable',
    'Device', 'CurrentNominal', 'CurrentBreaker',
    'OtherContact',

    'InsertTrans', 'UpdateTransOldSource', 'UpdateTransNewSource', 'UpdateTransRow', 'DeleteTrans',
    'InsertCable', 'UpdateCableOldSource', 'UpdateCableNewSource', 'UpdateCableRow', 'DeleteCable',
    'InsertContact', 'UpdateContactOldSource', 'UpdateContactNewSource', 'UpdateContactRow', 'DeleteContact',
    'InsertResist', 'UpdateResistOldSource', 'UpdateResistNewSource', 'UpdateResistRow', 'DeleteResist'
)


##########################
#       Main models      #
##########################
# 'Transformers' section #
##########################


class PowerNominal(BaseMixin, Base):
    """The class describes a table of transformer power nominals"""
    power = sa.orm.mapped_column(
        sa.Integer, nullable=False, unique=True, sort_order=10
    )

    # relationships
    transformers = sa.orm.relationship('Transformer', back_populates='power_nominals')


class VoltageNominal(BaseMixin, Base):
    """The class describes a table of transformer voltage nominals"""
    voltage = sa.orm.mapped_column(
        sa.Numeric(6, 3), nullable=False, unique=True, sort_order=10
    )

    # relationships
    transformers = sa.orm.relationship('Transformer', back_populates='voltage_nominals')


class Scheme(BaseMixin, Base):
    """The class describes a table of transformer vector group schemes"""
    vector_group = sa.orm.mapped_column(
        sa.String(10), nullable=False, unique=True, sort_order=10
    )

    # relationships
    transformers = sa.orm.relationship('Transformer', back_populates='schemes')


class Transformer(JoinedMixin, BaseMixin, Base):
    """The class describes a table of communication by transformers.

    Describes a table of communication by transformers, values of short circuit current
    powers and voltages, resistance and reactance of forward and reverse sequences.

    """

    SUBTABLES = PowerNominal, VoltageNominal, Scheme

    power_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            PowerNominal.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10
    )
    voltage_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            VoltageNominal.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10
    )
    vector_group_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            Scheme.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10
    )
    power_short_circuit = sa.orm.mapped_column(
        sa.Numeric(6, 3), nullable=False, sort_order=10
    )
    voltage_short_circuit = sa.orm.mapped_column(
        sa.Numeric(6, 3), nullable=False, sort_order=10
    )
    resistance_r1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    reactance_x1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    resistance_r0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    reactance_x0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )

    # relationships
    power_nominals = sa.orm.relationship('PowerNominal', back_populates='transformers')
    voltage_nominals = sa.orm.relationship('VoltageNominal', back_populates='transformers')
    schemes = sa.orm.relationship('Scheme', back_populates='transformers')


##############################
# 'Cables and wires' section #
##############################

class Mark(BaseMixin, Base):
    """The class describes a table of cable marking types"""
    mark_name = sa.orm.mapped_column(
        sa.String(20), nullable=False, unique=True, sort_order=10
    )

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='marks')


class Amount(BaseMixin, Base):
    """The class describes a table of the number of conductive cores of cables"""
    multicore_amount = sa.orm.mapped_column(
        sa.Integer, nullable=False, unique=True, sort_order=10
    )

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='amounts')


class RangeVal(BaseMixin, Base):
    """The class describes a table of cable ranges"""
    cable_range = sa.orm.mapped_column(
        sa.Numeric(4, 1), nullable=False, unique=True, sort_order=10
    )

    # relationships
    cables = sa.orm.relationship('Cable', back_populates='ranges')


class Cable(JoinedMixin, BaseMixin, Base):
    """The class describes a table of communication by cables.

    Describes a table of communication by cables, permissible values of long-term flowing
    current, resistance and reactance of forward and reverse sequences.

    """

    SUBTABLES = Mark, Amount, RangeVal

    mark_name_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            Mark.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10
    )
    multicore_amount_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            Amount.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10
    )
    cable_range_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            RangeVal.id, ondelete='CASCADE', onupdate='CASCADE'), sort_order=10
    )
    continuous_current = sa.orm.mapped_column(
        sa.Numeric(5, 2), nullable=False, sort_order=10
    )
    resistance_r1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    reactance_x1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    resistance_r0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    reactance_x0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )

    # relationships
    marks = sa.orm.relationship('Mark', back_populates='cables')
    amounts = sa.orm.relationship('Amount', back_populates='cables')
    ranges = sa.orm.relationship('RangeVal', back_populates='cables')


############################################
# 'Contacts and other resistances' section #
############################################

class Device(BaseMixin, Base):
    """The class describes a table of switching devices.

    Describes a table of switching devices: automatic current breaker, switches, etc.

    """
    device_type = sa.orm.mapped_column(
        sa.String(25), nullable=False, unique=True, sort_order=10
    )

    # relationships
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='devices')


class CurrentNominal(BaseMixin, Base):
    """The class describes a table of the switching devices current nominals"""
    current_value = sa.orm.mapped_column(
        sa.Integer, nullable=False, unique=True, sort_order=10
    )

    # relationships
    current_breakers = sa.orm.relationship('CurrentBreaker', back_populates='current_nominals')


class CurrentBreaker(JoinedMixin, BaseMixin, Base):
    """The class describes a table of the switching devices.

    Describes a table of the switching devices, it's device type id, current value id, resistances.

    """

    SUBTABLES = Device, CurrentNominal

    device_type_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            Device.id, ondelete='CASCADE', onupdate='CASCADE'
        ), sort_order=10)
    current_value_id = sa.orm.mapped_column(
        sa.Integer, sa.ForeignKey(
            CurrentNominal.id, ondelete='CASCADE', onupdate='CASCADE'
        ), sort_order=10)
    resistance_r1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    reactance_x1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=True, default=0, sort_order=10
    )
    resistance_r0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=True, default=0, sort_order=10
    )
    reactance_x0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=True, default=0, sort_order=10
    )

    # relationships
    devices = sa.orm.relationship('Device', back_populates='current_breakers')
    current_nominals = sa.orm.relationship('CurrentNominal', back_populates='current_breakers')


class OtherContact(BaseMixin, Base):
    """The class describes a table of the others resistances."""
    contact_type = sa.orm.mapped_column(
        sa.String(25), nullable=False, unique=True, sort_order=10
    )
    resistance_r1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=False, sort_order=10
    )
    reactance_x1 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=True, default=0, sort_order=10
    )
    resistance_r0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=True, default=0, sort_order=10
    )
    reactance_x0 = sa.orm.mapped_column(
        sa.Numeric(8, 5), nullable=True, default=0, sort_order=10
    )


###################################
# Dataclasses for CRUD operations #
###################################
#     'Transformers' section      #
###################################

@dataclass
class InsertTrans:
    power: int = field(default=Validator(log_info=True))
    voltage: Decimal = field(default=Validator(log_info=True))
    vector_group: str = field(default=Validator(log_info=True))

    power_short_circuit: Decimal = field(default=Validator(default=0))
    voltage_short_circuit: Decimal = field(default=Validator(default=0))
    resistance_r1: Decimal = field(default=Validator(default=0))
    reactance_x1: Decimal = field(default=Validator(default=0))
    resistance_r0: Decimal = field(default=Validator(default=0))
    reactance_x0: Decimal = field(default=Validator(default=0))


@dataclass
class UpdateTransOldSource:
    power: int = field(default=Validator())
    voltage: Decimal = field(default=Validator())
    vector_group: str = field(default=Validator())


@dataclass
class UpdateTransNewSource:
    power: int = field(default=Validator())
    voltage: Decimal = field(default=Validator())
    vector_group: str = field(default=Validator())


@dataclass
class UpdateTransRow:
    power_short_circuit: Decimal = field(default=Validator())
    voltage_short_circuit: Decimal = field(default=Validator())
    resistance_r1: Decimal = field(default=Validator())
    reactance_x1: Decimal = field(default=Validator())
    resistance_r0: Decimal = field(default=Validator())
    reactance_x0: Decimal = field(default=Validator())


@dataclass
class DeleteTrans:
    power: int = field(default=Validator())
    voltage: Decimal = field(default=Validator())
    vector_group: str = field(default=Validator())


##############################
# 'Cables and wires' section #
##############################

@dataclass
class InsertCable:
    mark_name: str = field(default=Validator(log_info=True))
    multicore_amount: int = field(default=Validator(log_info=True))
    cable_range: Decimal = field(default=Validator(log_info=True))

    continuous_current: Decimal = field(default=Validator(default=0))
    resistance_r1: Decimal = field(default=Validator(default=0))
    reactance_x1: Decimal = field(default=Validator(default=0))
    resistance_r0: Decimal = field(default=Validator(default=0))
    reactance_x0: Decimal = field(default=Validator(default=0))


@dataclass
class UpdateCableOldSource:
    mark_name: str = field(default=Validator())
    multicore_amount: int = field(default=Validator())
    cable_range: Decimal = field(default=Validator())


@dataclass
class UpdateCableNewSource:
    mark_name: str = field(default=Validator())
    multicore_amount: int = field(default=Validator())
    cable_range: Decimal = field(default=Validator())


@dataclass
class UpdateCableRow:
    continuous_current: Decimal = field(default=Validator())
    resistance_r1: Decimal = field(default=Validator())
    reactance_x1: Decimal = field(default=Validator())
    resistance_r0: Decimal = field(default=Validator())
    reactance_x0: Decimal = field(default=Validator())


@dataclass
class DeleteCable:
    mark_name: str = field(default=Validator())
    multicore_amount: int = field(default=Validator())
    cable_range: Decimal = field(default=Validator())


######################
# 'Contacts' section #
######################

@dataclass
class InsertContact:
    device_type: str = field(default=Validator(log_info=True))
    current_value: int = field(default=Validator(log_info=True))

    resistance_r1: Decimal = field(default=Validator(default=0))
    reactance_x1: Decimal = field(default=Validator(default=0))
    resistance_r0: Decimal = field(default=Validator(default=0))
    reactance_x0: Decimal = field(default=Validator(default=0))


@dataclass
class UpdateContactOldSource:
    device_type: str = field(default=Validator())
    current_value: int = field(default=Validator())


@dataclass
class UpdateContactNewSource:
    device_type: str = field(default=Validator())
    current_value: int = field(default=Validator())


@dataclass
class UpdateContactRow:
    resistance_r1: Decimal = field(default=Validator())
    reactance_x1: Decimal = field(default=Validator())
    resistance_r0: Decimal = field(default=Validator())
    reactance_x0: Decimal = field(default=Validator())


@dataclass
class DeleteContact:
    device_type: str = field(default=Validator())
    current_value: int = field(default=Validator())


###############################
# 'Other resistances' section #
###############################

@dataclass
class InsertResist:
    contact_type: str = field(default=Validator(log_info=True))

    resistance_r1: Decimal = field(default=Validator(default=0))
    reactance_x1: Decimal = field(default=Validator(default=0))
    resistance_r0: Decimal = field(default=Validator(default=0))
    reactance_x0: Decimal = field(default=Validator(default=0))


@dataclass
class UpdateResistOldSource:
    contact_type: str = field(default=Validator())


@dataclass
class UpdateResistNewSource:
    contact_type: str = field(default=Validator())


@dataclass
class UpdateResistRow:
    resistance_r1: Decimal = field(default=Validator())
    reactance_x1: Decimal = field(default=Validator())
    resistance_r0: Decimal = field(default=Validator())
    reactance_x0: Decimal = field(default=Validator())


@dataclass
class DeleteResist:
    contact_type: str = field(default=Validator())
