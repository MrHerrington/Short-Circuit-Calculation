# -*- coding: utf-8 -*-
"""This module contains classes for various electrical elements such as transformers, cables
and contacts, for programmatically inputting data related to these categories."""


import logging
import math
import typing as ty
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from functools import reduce

import sqlalchemy as sa

from ShortCircuitCalc.database import *
from ShortCircuitCalc.tools import session_scope
from ShortCircuitCalc.config import SYSTEM_VOLTAGE_IN_KILOVOLTS, CALCULATIONS_ACCURACY


__all__ = ('T', 'W', 'Q', 'QF', 'QS', 'R', 'Line', 'Arc', 'Calculator')


logger = logging.getLogger(__name__)


class Validator:
    """The class for validating the input data.

    The class for validating the input data in accordance with
    the type annotations specified when creating the dataclasses.

    Sample:
        @dataclass
        class Person:
            age: float = field(default=Validator())
            ---: ...

        print(Person('10').age) -> 10.0
        print(type(Person('10').age)) -> <class 'float'>

    """
    def __init__(self, arg=None) -> None:
        self._arg = arg

    def __set_name__(self, owner: ty.Any, name: ty.Any) -> None:
        self._public_name = name
        self._private_name = '_' + name

    def __get__(self, obj: ty.Any, owner: ty.Any) -> ty.Any:
        return getattr(obj, self._private_name)

    def __set__(self, obj: ty.Any, value: ty.Any) -> None:
        # https://stackoverflow.com/questions/67612451/combining-a-descriptor-class-with-dataclass-and-field
        # Next in Validator.__set__, when the arg argument is not provided to the
        # constructor, the value argument will actually be the instance of the
        # Validator class. So we need to change the guard to see if value is self:
        if value is self:
            value = self._arg
        else:
            try:
                value = ty.get_type_hints(obj)[self._public_name](value)
            except (TypeError, ValueError):
                msg = (f"The type of the attribute '{type(obj).__name__}.{self._public_name}' "
                       f'must be {ty.get_type_hints(obj)[self._public_name]}.')
                logger.error(msg)
                raise TypeError(msg)
        setattr(obj, self._private_name, value)


class BaseElement(ABC):
    """The abstract class for all elements"""
    __slots__ = ()

    @property
    def resistance_r1(self) -> Decimal:
        """The method searches in the database resistance R1."""
        query_val = self._sql_query('resistance_r1')
        if query_val is None:
            msg = 'The resistance R1 is not found in the database!'
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @property
    def reactance_x1(self) -> Decimal:
        """The method searches in the database reactance X1."""
        query_val = self._sql_query('reactance_x1')
        if query_val is None:
            msg = 'The reactance X1 is not found in the database!'
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @property
    def resistance_r0(self) -> Decimal:
        """The method searches in the database resistance R0."""
        query_val = self._sql_query('resistance_r0')
        if query_val is None:
            msg = 'The resistance R0 is not found in the database!'
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @property
    def reactance_x0(self) -> Decimal:
        """The method searches in the database reactance X0."""
        query_val = self._sql_query('reactance_x0')
        if query_val is None:
            msg = 'The reactance X0 is not found in the database!'
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @abstractmethod
    def _sql_query(self, attr_name) -> Decimal:
        """Returns the resistance value from the database.

        Args:
            attr_name (str): The attribute name to query.
        Returns:
            Decimal: The scalar value from the query.

        """
        pass


@dataclass
class T(BaseElement):
    """The class for transformer"""
    __slots__ = ('_power', '_vector_group')
    power: int = field(default=Validator())
    vector_group: str = field(default=Validator())
    voltage: Decimal = field(init=False, default=SYSTEM_VOLTAGE_IN_KILOVOLTS)

    def _sql_query(self, attr_name) -> Decimal:
        with session_scope() as session:
            return session.execute(sa.select(getattr(Transformer, attr_name)).
                                   join(PowerNominal, Transformer.power_id == PowerNominal.id).
                                   join(VoltageNominal, Transformer.voltage_id == VoltageNominal.id).
                                   join(Scheme, Transformer.vector_group_id == Scheme.id).
                                   where(sa.and_(PowerNominal.power == self.power,
                                                 VoltageNominal.voltage == self.voltage),
                                         Scheme.vector_group == self.vector_group)).scalar()


@dataclass
class W(BaseElement):
    """The class for cables and wires"""
    __slots__ = ('_mark', '_amount', '_range_val', '_length')
    mark: str = field(default=Validator())
    amount: int = field(default=Validator())
    range_val: float = field(default=Validator())
    # Length in meters
    length: int = field(default=Validator())

    def _sql_query(self, attr_name) -> Decimal:
        """Returns the resistance value for the specified length."""
        with session_scope() as session:
            query_val = session.execute(sa.select(getattr(Cable, attr_name)).
                                        join(Mark, Cable.mark_name_id == Mark.id).
                                        join(Amount, Cable.multicore_amount_id == Amount.id).
                                        join(RangeVal, Cable.cable_range_id == RangeVal.id).
                                        where(sa.and_(Mark.mark_name == self.mark,
                                                      Amount.multicore_amount == self.amount,
                                                      RangeVal.cable_range == self.range_val))).scalar()
        return query_val / 1000 * self.length


@dataclass
class Q(BaseElement):
    __slots__ = ('_device_type', '_current_value')
    current_value: int = field(default=Validator())
    device_type: str = field(default=Validator())

    def _sql_query(self, attr_name) -> Decimal:
        with session_scope() as session:
            return session.execute(sa.select(getattr(CurrentBreaker, attr_name)).
                                   join(Device, CurrentBreaker.device_type_id == Device.id).
                                   join(CurrentNominal, CurrentBreaker.current_value_id == CurrentNominal.id).
                                   where(sa.and_(Device.device_type == self.device_type,
                                                 CurrentNominal.current_value == self.current_value))).scalar()


@dataclass
class QF(Q):
    def __post_init__(self):
        self.device_type = 'Автомат'


@dataclass
class QS(Q):
    def __post_init__(self):
        self.device_type = 'Рубильник'


@dataclass
class R(BaseElement):
    __slots__ = '_contact_type'
    contact_type: str = field(default=Validator())

    def _sql_query(self, attr_name) -> Decimal:
        with session_scope() as session:
            return session.execute(sa.select(getattr(OtherContact, attr_name)).
                                   where(OtherContact.contact_type == self.contact_type)).scalar()


@dataclass
class Line(R):
    def __post_init__(self):
        self.contact_type = 'РУ'


@dataclass
class Arc(R):
    def __post_init__(self):
        self.contact_type = 'Дуга'


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
