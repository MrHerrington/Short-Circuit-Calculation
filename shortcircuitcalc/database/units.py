# -*- coding: utf-8 -*-
"""
This module contains classes and dataclasses for various electrical
elements such as transformers, cables and contacts, for
programmatically inputting data related to these categories.

Classes:
    - BaseElement: The abstract class for all elements.

    - T: The dataclass describes transformer.
    - W: The dataclass describes cables/wires.
    - Q: The dataclass describes current breaker devices if default device type is not defined.
    - QF: The dataclass describes current breaker devices if default device type is 'Автомат'.
    - QS: The dataclass describes current breaker devices if default device type is 'Рубильник'.
    - R: The dataclass describes other contacts if default contact type is not defined.
    - Line: The dataclass describes other contacts has default contact type 'РУ'.
    - Arc: The dataclass describes other contacts has default contact type 'Дуга'.

"""


import logging
from decimal import Decimal
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import sqlalchemy as sa

from shortcircuitcalc.tools import Validator, session_scope, config_manager
from shortcircuitcalc.database.models import (
    PowerNominal, VoltageNominal, Scheme, Transformer,
    Mark, Amount, RangeVal, Cable,
    Device, CurrentNominal, CurrentBreaker,
    OtherContact
)


__all__ = (
    'BaseElement',
    'T', 'W', 'Q', 'QF', 'QS', 'R', 'Line', 'Arc',
)


logger = logging.getLogger(__name__)


class BaseElement(ABC):
    """
    The abstract class for all elements.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    """
    __slots__ = ()

    @property
    def resistance_r1(self) -> Decimal:
        """
        The method searches in the database resistance R1.

        """
        query_val = self._sql_query('resistance_r1')
        if query_val is None:
            msg = f"The resistance R1 for '{self}' is not found in the database!"
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @property
    def reactance_x1(self) -> Decimal:
        """
        The method searches in the database reactance X1.

        """
        query_val = self._sql_query('reactance_x1')
        if query_val is None:
            msg = f"The reactance X1 for '{self}' is not found in the database!"
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @property
    def resistance_r0(self) -> Decimal:
        """
        The method searches in the database resistance R0.

        """
        query_val = self._sql_query('resistance_r0')
        if query_val is None:
            msg = f"The resistance R0 for '{self}' is not found in the database!"
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @property
    def reactance_x0(self) -> Decimal:
        """
        The method searches in the database reactance X0.

        """
        query_val = self._sql_query('reactance_x0')
        if query_val is None:
            msg = f"The reactance X0 for '{self}' is not found in the database!"
            logger.error(msg)
            raise ValueError(msg)
        return query_val

    @abstractmethod
    def _sql_query(self, attr_name) -> Decimal:
        """
        Returns the resistance value from the database.

        Args:
            attr_name (str): The attribute name to query.
        Returns:
            Decimal: The scalar value from the query.

        """
        pass


@dataclass
class T(BaseElement):
    """
    The dataclass describes transformer.

    The dataclass describes transformer. Using the
    decorator 'Validator' also takes a string value.

    Attributes:
        power (Union[int, str]): The nominal power of the transformer.
        voltage (Union[Decimal, str]): The nominal voltage of the transformer.
        vector_group (str): The vector group of the transformer.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Samples string representation:
        - print(T(63, 'У/Ун-0')) -> T 63/0.4 (У/Ун-0)
        - print(T('160', 'Д/Ун-11')) -> T 160/0.4 (Д/Ун-11)

    """
    __slots__ = ('_power', '_vector_group')
    power: int = field(default=Validator())
    vector_group: str = field(default=Validator())
    voltage: Decimal = field(init=False, default=config_manager('SYSTEM_VOLTAGE_IN_KILOVOLTS'))

    def _sql_query(self, attr_name) -> Decimal:
        """
        Returns the resistance value from the database.

        Args:
            attr_name (str): The attribute name to query.
        Returns:
            Decimal: The scalar value from the query.

        """
        with session_scope() as session:
            return session.execute(
                sa.select(
                    getattr(Transformer, attr_name)
                ).join(
                    PowerNominal, Transformer.power_id == PowerNominal.id
                ).join(
                    VoltageNominal, Transformer.voltage_id == VoltageNominal.id
                ).join(
                    Scheme, Transformer.vector_group_id == Scheme.id
                ).where(
                    sa.and_(
                        PowerNominal.power == self.power,
                        VoltageNominal.voltage == self.voltage,
                        Scheme.vector_group == self.vector_group
                    )
                )
            ).scalar()

    def __str__(self):
        return f'T {self.power}/{float(self.voltage)} ({self.vector_group})'


@dataclass
class W(BaseElement):
    """
    The dataclass describes cables and wires.

    The dataclass describes cables and wires. Using the
    decorator 'Validator' also takes a string value.

    Attributes:
        mark (str): The mark name of the cable/wire.
        amount (Union[int, str]): The multicore amount of the cable/wire.
        range_val (Union[Decimal, str]): The range value of the cable/wire.
        length (int): The length of the cable/wire in meters.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Samples string representation:
        - print(W('ВВГ', 3, 2.5, 50)) -> ВВГ 3x2.5 50м
        - print(W('СИП', '3', '120', '100')) -> СИП 3x120 100м

    """
    __slots__ = ('_mark', '_amount', '_range_val', '_length')
    mark: str = field(default=Validator())
    amount: int = field(default=Validator())
    range_val: Decimal = field(default=Validator())
    # Length in meters
    length: int = field(default=Validator())

    def _sql_query(self, attr_name) -> Decimal:
        """
        Returns the resistance value from the database.

        Args:
            attr_name (str): The attribute name to query.
        Returns:
            Decimal: The scalar value from the query.

        """
        with session_scope() as session:
            query_val = session.execute(
                sa.select(
                    getattr(Cable, attr_name)
                ).join(
                    Mark, Cable.mark_name_id == Mark.id
                ).join(
                    Amount, Cable.multicore_amount_id == Amount.id
                ).join(
                    RangeVal, Cable.cable_range_id == RangeVal.id
                ).where(
                    sa.and_(
                        Mark.mark_name == self.mark,
                        Amount.multicore_amount == self.amount,
                        RangeVal.cable_range == self.range_val
                    )
                )
            ).scalar()
        return query_val / 1000 * self.length

    def __str__(self):
        if int(self.range_val) == float(self.range_val):
            return f'{self.mark} {self.amount}х{int(self.range_val)} {self.length}m'
        else:
            return f'{self.mark} {self.amount}х{self.range_val} {self.length}m'


@dataclass
class Q(BaseElement):
    """
    The dataclass describes current breaker devices if default device type is not defined.

    The dataclass describes current breaker devices if default device type is
    not defined. Using the decorator 'Validator' also takes a string value.

    Attributes:
        current_value (Union[int, str]): The nominal current value of current breaker device.
        device_type (str): The device type of the current breaker.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Samples string representation:
        - print(Q(25, 'Устройство')) -> Q 25A
        - print(Q('63', 'Контактор')) -> Q 63A

    """
    __slots__ = ('_device_type', '_current_value')
    current_value: int = field(default=Validator())
    device_type: str = field(default=Validator())

    def _sql_query(self, attr_name) -> Decimal:
        """
        Returns the resistance value from the database.

        Args:
            attr_name (str): The attribute name to query.
        Returns:
            Decimal: The scalar value from the query.

        """
        with session_scope() as session:
            return session.execute(
                sa.select(
                    getattr(CurrentBreaker, attr_name)
                ).join(
                    Device, CurrentBreaker.device_type_id == Device.id
                ).join(
                    CurrentNominal, CurrentBreaker.current_value_id == CurrentNominal.id
                ).where(
                    sa.and_(
                        Device.device_type == self.device_type,
                        CurrentNominal.current_value == self.current_value
                    )
                )
            ).scalar()

    def __str__(self):
        return f'Q {self.current_value}A'


@dataclass
class QF(Q):
    """
    The dataclass describes current breaker devices has default device type 'Автомат'.

    Attributes:
        current_value (Union[int, str]): The nominal current value of current breaker device.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Sample string representation:
        - print(QF(25)) -> QF 25A
        - print(QF('63')) -> QF 63A

    """

    def __post_init__(self):
        self.device_type = 'Автомат'

    def __str__(self):
        return f'QF {self.current_value}A'


@dataclass
class QS(Q):
    """
    The dataclass describes current breaker devices has default device type 'Рубильник'.

    Attributes:
        current_value (Union[int, str]): The nominal current value of current breaker device.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Sample string representation:
        - print(QS(25)) -> QS 25A
        - print(QS('63')) -> QS 63A

    """

    def __post_init__(self):
        self.device_type = 'Рубильник'

    def __str__(self):
        return f'QS {self.current_value}A'


@dataclass
class R(BaseElement):
    """
    The dataclass describes other contacts if default contact type is not defined.

    Attributes:
        contact_type (str): The contact type of the other contact.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Sample string representation:
        - print(R('Клеммник')) -> R

    """
    __slots__ = '_contact_type'
    contact_type: str = field(default=Validator())

    def _sql_query(self, attr_name) -> Decimal:
        with session_scope() as session:
            return session.execute(
                sa.select(
                    getattr(OtherContact, attr_name)
                ).where(
                    OtherContact.contact_type == self.contact_type
                )
            ).scalar()

    def __str__(self):
        return 'R'


@dataclass
class Line(R):
    """
    The dataclass describes other contacts has default contact type 'РУ'.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Sample string representation:
        - print(Line()) -> РУ

    """

    def __post_init__(self):
        self.contact_type = 'РУ'

    def __str__(self):
        return f'{self.contact_type}'


@dataclass
class Arc(R):
    """
    The dataclass describes other contacts has default contact type 'Дуга'.

    Public properties:
        - resistance_r1: The method searches in the database resistance R1.
        - reactance_x1: The method searches in the database reactance X1.
        - resistance_r0: The method searches in the database resistance R0.
        - reactance_x0: The method searches in the database reactance X0.

    Sample string representation:
        - print(Arc()) -> Дуга

    """

    def __post_init__(self):
        self.contact_type = 'Дуга'

    def __str__(self):
        return f'{self.contact_type}'
