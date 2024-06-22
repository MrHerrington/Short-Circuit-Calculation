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

    - ElemChain: The class describes the chain of elements.
    - ChainsSystem: The class describes system of chains of elements.

"""


import logging
import math
import re
import typing as ty
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from functools import reduce

import sqlalchemy as sa

from shortcircuitcalc.tools.tools import Validator, session_scope, config_manager
from shortcircuitcalc.database import (
    PowerNominal, VoltageNominal, Scheme, Transformer,
    Mark, Amount, RangeVal, Cable,
    Device, CurrentNominal, CurrentBreaker,
    OtherContact
)


__all__ = (
    'BaseElement',
    'T', 'W', 'Q', 'QF', 'QS', 'R', 'Line', 'Arc',
    'ElemChain', 'ChainsSystem'
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


class ElemChain(ty.Sequence, ty.Mapping):
    # noinspection PyUnresolvedReferences
    """
    The class describes the chain of elements.

    Attributes:
        obj (Union[Sequence, Mapping]): The chain of elements.

    Public properties:
        - three_phase_current_short_circuit: The method calculates the three-phase current during a short circuit.
        - two_phase_current_short_circuit: The method calculates the two-phase current during a short circuit.
        - one_phase_current_short_circuit: The method calculates the one-phase current during a short circuit.

    Samples data input as sequence:
        - ElemChain((QS(63), QF(25), Line()))
        - ElemChain([QS(63), W('ВВГ', 3, 2.5, 50)])

    Samples data input as mapping:
        - ElemChain({QS1: QS(63), QF1: QF(25), R1: Line()})
        - ElemChain({QS1: QS(63), W1: W('ВВГ', 3, 2.5, 50)})

    """

    def __init__(self, obj: ty.Union[ty.Sequence, ty.Mapping]) -> None:
        self._obj = obj

    @property
    def obj(self) -> ty.Union[ty.Sequence, ty.Mapping]:
        return self._obj

    @property
    def three_phase_current_short_circuit(self) -> Decimal:
        """
        Calculates the three-phase current during a short circuit.

        Returns:
            Decimal: The calculated three-phase current during a short circuit.

        .. math::
            I_{k^{(3)}} = \\frac{U}{\\sqrt{3} * z_{^{(3)}}}
        :math:`U` - voltage value,
        :math:`z_{^{(3)}}` - three-phase summary resistance.

        """
        return round(
            (
                config_manager('SYSTEM_VOLTAGE_IN_KILOVOLTS') / Decimal(math.sqrt(3)) /
                self.__three_phase_summary_resistance()
            ),
            config_manager('CALCULATIONS_ACCURACY')
        )

    @property
    def two_phase_current_short_circuit(self) -> Decimal:
        """
        Calculates the two-phase current during a short circuit.

        Returns:
            Decimal: The calculated two-phase current during a short circuit.

        .. math::
            I_{k^{(2)}} = \\frac{\\sqrt{3} * I_{k^{(3)}}}{2}
        :math:`I_{k^{(3)}}` - three-phase current during a short circuit.

        """
        return round(
            (
                Decimal(math.sqrt(3)) / 2 * self.three_phase_current_short_circuit
            ),
            config_manager('CALCULATIONS_ACCURACY')
        )

    @property
    def one_phase_current_short_circuit(self) -> Decimal:
        """
        Calculates the one-phase current during a short circuit.

        Returns:
            Decimal: The calculated one-phase current during a short circuit.

        .. math::
            I_{k^{(1)}} = \\frac{\\sqrt{3} * U}{z_{^{(1)}}}
        :math:`U` - voltage value,
        :math:`I_{k^{(1)}}` - one-phase current during a short circuit.

        """
        return round(
            (
                Decimal(math.sqrt(3)) * config_manager('SYSTEM_VOLTAGE_IN_KILOVOLTS') /
                self.__one_phase_summary_resistance()
            ),
            config_manager('CALCULATIONS_ACCURACY')
        )

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
        def __summary_resistance(obj: ty.Union[ty.Sequence, dict.values]) -> Decimal:
            """
            Service function, calculates summary resistance.

            Args:
                obj (Union[Sequence, Mapping]): The chain of elements.
            Returns:
                summary resistance as single Decimal value.

            """
            return Decimal(
                math.sqrt(
                    math.pow(
                        reduce(
                            lambda x, y: x + y, (i.resistance_r1 for i in obj)
                        ), 2
                    ) +
                    math.pow(
                        reduce(
                            lambda x, y: x + y, (i.reactance_x1 for i in obj)
                        ), 2
                    )
                )
            )

        if isinstance(self.obj, ty.Sequence):
            return __summary_resistance(self.obj)

        if isinstance(self.obj, ty.Mapping):
            return __summary_resistance(self.obj.values())

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
        def __summary_resistance(obj: ty.Union[ty.Sequence, dict.values]) -> Decimal:
            """
            Service function, calculates summary resistance.

            Args:
                obj (Union[Sequence, Mapping]): The chain of elements.
            Returns:
                summary resistance as single Decimal value.

            """
            return Decimal(
                math.sqrt(
                    math.pow(
                        2 * reduce(
                            lambda x, y: x + y, (i.resistance_r1 for i in obj)
                        ) +
                        reduce(
                            lambda x, y: x + y, (i.resistance_r0 for i in obj)
                        ), 2
                    ) +
                    math.pow(
                        2 * reduce(
                            lambda x, y: x + y, (i.reactance_x1 for i in obj)
                        ) +
                        reduce(
                            lambda x, y: x + y, (i.reactance_x0 for i in obj)
                        ), 2
                    )
                )
            )

        if isinstance(self.obj, ty.Sequence):
            return __summary_resistance(self.obj)

        if isinstance(self.obj, ty.Mapping):
            return __summary_resistance(self.obj.values())

    def __getitem__(self, key):
        if isinstance(self.obj, ty.Sequence):
            if isinstance(key, slice):
                return ElemChain(self.obj[key])
            else:
                return self.obj[key]

        if isinstance(self.obj, ty.Mapping):
            if isinstance(key, slice):
                return ElemChain(dict(tuple(self.obj.items())[key]))
            else:
                return dict((tuple(self.obj.items())[key],))

    def __len__(self):
        return len(self.obj)

    def __str__(self):
        if isinstance(self.obj, ty.Sequence):
            return f"{' -> '.join(map(str, self.obj))}"

        if isinstance(self.obj, ty.Mapping):
            return f"{' -> '.join('%s: %s' % (key, value) for key, value in zip(self.obj.keys(), self.obj.values()))}"

    def __repr__(self):
        return f"ElemChain{self.obj}"


class ChainsSystem(ty.Iterable):
    # noinspection PyUnresolvedReferences
    """
    The class describes system of chains of elements.

    The class describes system of chains of elements. If input argument has
    string type, it will be parsed to the system of chains of elements.

    Attributes:
        obj (Union[Iterable, str]): The system of chains of elements.

    Samples:
        - ChainsSystem([
            ElemChain([T(160, 'У/Ун-0'), QS(160), QF(160)]),
            ElemChain([QF(25)])
          ])
        - ChainsSystem([
            ElemChain({'T1': T(160, 'У/Ун-0'), 'QS1': QS(160), 'QF1': QF(160)}),
            ElemChain([QF(25)])
          ])
        - ChainsSystem(
            "T(160, 'У/Ун-0'), QS(160), QF(160), Line(), QF(25), W('ВВГ', 3, 4, 20), Line(), Arc();"
            "TCH: T(160, 'У/Ун-0'), QF3: QF(100), R1: Line(), QF2: QF(25), W1: W('ВВГ', 3, 4, 20)"
          )


    """
    def __init__(self, obj):
        self.obj = obj
        if isinstance(self.obj, str):
            self.__parse_obj__()

    def __parse_obj__(self):
        """
        Service method parse obj argument into ElemChain objects if it has string type.

        """
        # regex patterns
        delimiter_pattern = r';\s*(?![^(]*\))'
        iterable_pattern = r'(?P<type>\w+)\((?P<args>.*?)\)'
        mapping_pattern = r'((?P<name>\w+):)\s*(?P<type>\w+)\((?P<args>.*?)\)'

        # split chains
        chains = re.split(delimiter_pattern, self.obj)

        for n in range(len(chains)):
            chain = tuple(re.finditer(mapping_pattern, chains[n]))
            if chain:
                chains[n] = ElemChain(
                    dict(
                        map(
                            lambda elem: (
                                elem.group('name'), globals()[elem.group('type')](
                                    *[x.strip('\'\"') for x in elem.group('args').split(', ')]
                                )
                            ), chain
                        )
                    )
                )
            else:
                chain = tuple(re.finditer(iterable_pattern, chains[n]))
                chains[n] = ElemChain(
                    tuple(
                        map(
                            lambda elem: globals()[elem.group('type')](
                                *[x.strip('\'\"') for x in elem.group('args').split(', ')]
                            ),
                            chain
                        )
                    )
                )
        self.obj = chains

    def __iter__(self):
        return iter(self.obj)

    def __len__(self):
        return len(self.obj)

    def __str__(self):
        return f"[ChainsSystem of {len(self.obj)} chains / {sum(map(len, self.obj))} elements]"

    def __repr__(self):
        return f'ChainsSystem{self.obj}'
