# from abc import ABC, abstractmethod
from dataclasses import dataclass, field
# from decimal import Decimal
# from ShortCircuitCalc.tools import session_scope
# from ShortCircuitCalc.database.transformer import *


@dataclass
class T:
    __slots__ = ('power', 'voltage', 'vector_group')
    power: int
    voltage: float
    vector_group: str


@dataclass
class Q:
    __slots__ = ('device_type', 'current_value')
    current_value: int
    device_type: str


@dataclass
class QF(Q):
    device_type: str = field(default='Автомат')


@dataclass
class QS(Q):
    device_type: str = field(default='Рубильник')


# with session_scope() as session:
#     pass

print(QS(25))
