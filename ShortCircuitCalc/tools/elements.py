# -*- coding: utf-8 -*-
"""This module contains classes for various electrical elements such as transformers, cables
and contacts, for programmatically inputting data related to these categories."""


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
import typing as ty
import math
from functools import reduce
import sqlalchemy as sa
from ShortCircuitCalc.tools import session_scope
from ShortCircuitCalc.config import SYSTEM_VOLTAGE_IN_KILOVOLTS, CALCULATIONS_ACCURACY
import ShortCircuitCalc.database as db


class BaseElement(ABC):
    """The abstract class for all elements"""
    __slots__ = ()

    @property
    def resistance_r1(self) -> Decimal:
        """The method searches in the database resistance R1."""
        query_val = self._sql_query('resistance_r1')
        if query_val is None:
            raise ValueError('The resistance R1 is not found in the database!')
        return query_val

    @property
    def reactance_x1(self) -> Decimal:
        """The method searches in the database reactance X1."""
        query_val = self._sql_query('reactance_x1')
        if query_val is None:
            raise ValueError('The reactance X1 is not found in the database!')
        return query_val

    @property
    def resistance_r0(self) -> Decimal:
        """The method searches in the database resistance R0."""
        query_val = self._sql_query('resistance_r0')
        if query_val is None:
            raise ValueError('The resistance R0 is not found in the database!')
        return query_val

    @property
    def reactance_x0(self) -> Decimal:
        """The method searches in the database reactance X0."""
        query_val = self._sql_query('reactance_x0')
        if query_val is None:
            raise ValueError('The reactance X0 is not found in the database!')
        return query_val

    @abstractmethod
    def _sql_query(self, attr_name) -> 'sa.scalar':
        """Returns the resistance value from the database.

        Args:
            attr_name (str): The attribute name to query.
        Returns:
            sa.scalar: The scalar value from the query.

        """
        pass


@dataclass
class T(BaseElement):
    """The class for transformer"""
    __slots__ = ('power', 'vector_group')
    power: int
    vector_group: str
    voltage: Decimal = field(init=False, default=SYSTEM_VOLTAGE_IN_KILOVOLTS)

    def _sql_query(self, attr_name) -> 'sa.scalar':
        with session_scope() as session:
            return session.execute(sa.select(getattr(db.Transformer, attr_name)).
                                   join(db.PowerNominal, db.Transformer.power_id == db.PowerNominal.id).
                                   join(db.VoltageNominal, db.Transformer.voltage_id == db.VoltageNominal.id).
                                   join(db.Scheme, db.Transformer.vector_group_id == db.Scheme.id).
                                   where(sa.and_(db.PowerNominal.power == self.power,
                                                 db.VoltageNominal.voltage == self.voltage),
                                         db.Scheme.vector_group == self.vector_group)).scalar()


@dataclass
class W(BaseElement):
    """The class for cables and wires"""
    __slots__ = ('mark', 'amount', 'range_val', 'length')
    mark: str
    amount: int
    range_val: float
    # Length in meters
    length: int

    def _sql_query(self, attr_name) -> 'sa.scalar':
        """Returns the resistance value for the specified length."""
        with session_scope() as session:
            query_val = session.execute(sa.select(getattr(db.Cable, attr_name)).
                                        join(db.Mark, db.Cable.mark_name_id == db.Mark.id).
                                        join(db.Amount, db.Cable.multicore_amount_id == db.Amount.id).
                                        join(db.RangeVal, db.Cable.cable_range_id == db.RangeVal.id).
                                        where(sa.and_(db.Mark.mark_name == self.mark,
                                                      db.Amount.multicore_amount == self.amount,
                                                      db.RangeVal.cable_range == self.range_val))).scalar()
        return query_val / 1000 * self.length


@dataclass
class Q(BaseElement):
    __slots__ = ('device_type', 'current_value')
    current_value: int
    device_type: str

    def _sql_query(self, attr_name) -> 'sa.scalar':
        with session_scope() as session:
            return session.execute(sa.select(getattr(db.CurrentBreaker, attr_name)).
                                   join(db.Device, db.CurrentBreaker.device_type_id == db.Device.id).
                                   join(db.CurrentNominal, db.CurrentBreaker.current_value_id == db.CurrentNominal.id).
                                   where(sa.and_(db.Device.device_type == self.device_type,
                                                 db.CurrentNominal.current_value == self.current_value))).scalar()


@dataclass
class QF(Q):
    device_type: str = field(default='Автомат')


@dataclass
class QS(Q):
    device_type: str = field(default='Рубильник')


@dataclass
class R(BaseElement):
    __slots__ = 'contact_type'
    contact_type: str

    def _sql_query(self, attr_name) -> 'sa.scalar':
        with session_scope() as session:
            return session.execute(sa.select(getattr(db.OtherContact, attr_name)).
                                   where(db.OtherContact.contact_type == self.contact_type)).scalar()


class Calculator:
    """The class for short circuit calculations"""

    def __init__(self, obj: ty.Sequence[BaseElement]) -> None:
        self._obj = obj

    @property
    def obj(self) -> ty.Sequence[BaseElement]:
        return self._obj

    @property
    def three_phase_current_short_circuit(self) -> Decimal:
        """Calculates the three-phase current during a short circuit.

        Returns:
            Decimal: The calculated three-phase current during a short circuit.
        .. math::
            I_{k^{(3)}} = \\frac{U}{\\sqrt{3} * z_{^{(3)}}}
        :math:`U` - voltage value,
        :math:`z_{^{(3)}}` - three-phase summary resistance.

        """
        return round(
            SYSTEM_VOLTAGE_IN_KILOVOLTS / Decimal(math.sqrt(3)) / self.__three_phase_summary_resistance(),
            CALCULATIONS_ACCURACY)

    @property
    def two_phase_voltage_short_circuit(self) -> Decimal:
        """Calculates the two-phase current during a short circuit.

        Returns:
            Decimal: The calculated two-phase current during a short circuit.
        .. math::
            I_{k^{(2)}} = \\frac{\\sqrt{3} * I_{k^{(3)}}}{2}
        :math:`I_{k^{(3)}}` - three-phase current during a short circuit.

        """
        return round(
            Decimal(math.sqrt(3)) / 2 * self.three_phase_current_short_circuit,
            CALCULATIONS_ACCURACY)

    @property
    def one_phase_voltage_short_circuit(self) -> Decimal:
        """Calculates the one-phase current during a short circuit.

        Returns:
            Decimal: The calculated one-phase current during a short circuit.
        .. math::
            I_{k^{(1)}} = \\frac{\\sqrt{3} * U}{z_{^{(1)}}}
        :math:`U` - voltage value,
        :math:`I_{k^{(1)}}` - one-phase current during a short circuit.

        """
        return round(
            Decimal(math.sqrt(3)) * SYSTEM_VOLTAGE_IN_KILOVOLTS / self.__one_phase_summary_resistance(),
            CALCULATIONS_ACCURACY)

    def __three_phase_summary_resistance(self) -> Decimal:
        """
        Service function, calculates three-phase summary resistance.

        Returns:
            single Decimal value.
        .. math::
            z_{^{(3)}} = \\sqrt{r_{1\\sum_{}^{2}} + x_{1\\sum_{}^{2}}}
        :math:`r_1` - resistance value resistance_r1,
        :math:`x_1` - reactance value reactance_x1.

        """
        return Decimal(math.sqrt(math.pow(
            reduce(lambda x, y: x + y, (
                i.resistance_r1 for i in self.obj)), 2) + math.pow(
            reduce(lambda x, y: x + y, (
                i.reactance_x1 for i in self.obj)), 2)))

    def __one_phase_summary_resistance(self) -> Decimal:
        """
        Service function, calculates one-phase summary resistance.

        Returns:
            single Decimal value.
        .. math::
            z_{^{(1)}} = \\sqrt{{(2r_{1\\sum_{}} + r_{0\\sum_{}})}^{2} + {(2x_{1\\sum_{}} + x_{0\\sum_{}})}^{2}}
        :math:`r_1` - resistance value resistance_r1,
        :math:`r_0` - resistance value resistance_r0,
        :math:`x_1` - reactance value reactance_x1,
        :math:`x_0` - reactance value reactance_x0.

        """
        return Decimal(math.sqrt(
            math.pow(
                2 * reduce(lambda x, y: x + y, (i.resistance_r1 for i in self.obj)) +
                reduce(lambda x, y: x + y, (i.resistance_r0 for i in self.obj)), 2) +
            math.pow(
                2 * reduce(lambda x, y: x + y, (i.reactance_x1 for i in self.obj)) +
                reduce(lambda x, y: x + y, (i.reactance_x0 for i in self.obj)), 2)))


# print(T(25, 'У/Ун-0').resistance_r1)
# print(T(25, 'У/Ун-0').reactance_x1)
# print(T(25, 'У/Ун-0').resistance_r0)
# print(T(25, 'У/Ун-0').reactance_x0)
# print()
#
# print(W('СИП', 3, 120, 1000).resistance_r1)
# print(W('СИП', 3, 120, 1000).reactance_x1)
# print(W('СИП', 3, 120, 1000).resistance_r0)
# print(W('СИП', 3, 120, 1000).reactance_x0)
# print()
#
# print(Q(4, 'Автомат').resistance_r1)
# print(QF(4).resistance_r1)
# print(QS(4).resistance_r1)
# print()
#
# print(R('РУ').resistance_r1)
# D = R('Дуга').one_phase_voltage_short_circuit)

# TCH = T(160, 'У/Ун-0')
# print(Calculator((TCH, D)).three_phase_current_short_circuit)
# print(Calculator((TCH, D)).two_phase_voltage_short_circuit)
# print(Calculator((TCH, D))
