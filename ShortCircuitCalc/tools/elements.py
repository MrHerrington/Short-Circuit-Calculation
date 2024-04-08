"""This module contains classes for various electrical elements such as transformers, cables
and contacts, for programmatically inputting data related to these categories."""


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from ShortCircuitCalc.tools import session_scope
from ShortCircuitCalc.database.transformer import *
from ShortCircuitCalc.database.cable import *
from ShortCircuitCalc.database.contact import *


class BaseElement(ABC):
    """The abstract class for all elements"""
    __slots__ = ()

    def resistance_r1(self) -> Decimal:
        """The method searches in the database resistance R1."""
        query_val = self.sql_query('resistance_r1')
        if query_val:
            return query_val
        else:
            raise ValueError('The resistance R1 is not found in the database!')

    def reactance_x1(self) -> Decimal:
        """The method searches in the database reactance X1."""
        query_val = self.sql_query('reactance_x1')
        if query_val:
            return query_val
        else:
            raise ValueError('The reactance X1 is not found in the database!')

    def resistance_r0(self) -> Decimal:
        """The method searches in the database resistance R0."""
        query_val = self.sql_query('resistance_r0')
        if query_val:
            return query_val
        else:
            raise ValueError('The resistance R0 is not found in the database!')

    def reactance_x0(self) -> Decimal:
        """The method searches in the database reactance X0."""
        query_val = self.sql_query('reactance_x0')
        if query_val:
            return query_val
        else:
            raise ValueError('The reactance X0 is not found in the database!')

    @abstractmethod
    def sql_query(self, attr_name) -> 'sa.scalar':
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
    __slots__ = ('power', 'voltage', 'vector_group')
    power: int
    voltage: float
    vector_group: str

    def sql_query(self, attr_name) -> 'sa.scalar':
        with session_scope() as session:
            return session.execute(sa.select(getattr(Transformer, attr_name)).
                                   join(PowerNominal, Transformer.power_id == PowerNominal.id).
                                   join(VoltageNominal, Transformer.voltage_id == VoltageNominal.id).
                                   join(Scheme, Transformer.vector_group_id == Scheme.id).
                                   where(sa.and_(PowerNominal.power == self.power,
                                                 VoltageNominal.voltage == Decimal(str(self.voltage)),
                                                 Scheme.vector_group == self.vector_group))).scalar()


@dataclass
class W(BaseElement):
    """The class for cables and wires"""
    __slots__ = ('mark', 'amount', 'range_val', 'length')
    mark: str
    amount: int
    range_val: float
    # length in meters
    length: int

    def sql_query(self, attr_name) -> 'sa.scalar':
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
    __slots__ = ('device_type', 'current_value')
    current_value: int
    device_type: str

    def sql_query(self, attr_name) -> 'sa.scalar':
        with session_scope() as session:
            return session.execute(sa.select(getattr(CurrentBreaker, attr_name)).
                                   join(Device, CurrentBreaker.device_type_id == Device.id).
                                   join(CurrentNominal, CurrentBreaker.current_value_id == CurrentNominal.id).
                                   where(sa.and_(Device.device_type == self.device_type,
                                                 CurrentNominal.current_value == self.current_value))).scalar()


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

    def sql_query(self, attr_name) -> 'sa.scalar':
        with session_scope() as session:
            return session.execute(sa.select(getattr(OtherContact, attr_name)).
                                   where(OtherContact.contact_type == self.contact_type)).scalar()


print(T(25, 0.4, 'У/Ун-0').resistance_r1())
print(T(25, 0.4, 'У/Ун-0').reactance_x1())
print(T(25, 0.4, 'У/Ун-0').resistance_r0())
print(T(25, 0.4, 'У/Ун-0').reactance_x0())
print()

print(W('СИП', 3, 120, 1000).resistance_r1())
print(W('СИП', 3, 120, 1000).reactance_x1())
print(W('СИП', 3, 120, 1000).resistance_r0())
print(W('СИП', 3, 120, 1000).reactance_x0())
print()

print(Q(4, 'Автомат').resistance_r1())
print(QF(4).resistance_r1())
print(QS(4).resistance_r1())
print()

print(R('Дуга').resistance_r1())
print(R('РУ').resistance_r1())
